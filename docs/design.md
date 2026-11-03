# Technical Design

## 1. Shape of the system

```mermaid
flowchart LR
  B[Browser] -->|HTTPS| T[Traefik]
  T -->|/| N[Next.js SSR]
  T -->|/api, /admin| D[Django + Ninja]
  N -->|server-side fetch| D
  D --> PG[(PostgreSQL 16)]
  D --> R[(Redis 7)]
  D --> MQ[(RabbitMQ)]
  D --> S3[(S3 / MinIO)]
  D -->|SSE| B
  MQ --> J[Celery judge worker]
  J --> GJ[go-judge]
  J --> SQ[(SQL-judge PostgreSQL)]
  J --> S3
  J -->|result callback| D
```

Two VMs. Everything stateful that matters (Postgres, Redis, RabbitMQ) lives on the app
server; the judge server holds go-judge and a throwaway Postgres. The judge server
accepts traffic only from the app server.

**Why a modular monolith.** Under 1,000 users, three developers, twelve weeks. Splitting
`commerce` from `catalog` into services buys distributed transactions and on-call load for
no benefit. Module boundaries are enforced by convention (service functions, domain
events) and reviewed in PRs, which is enough structure to extract a service later if
judging volume demands it.

**Why the judge is separate anyway.** It is the one component whose failure mode is
"arbitrary code". Keeping it off the database host means a sandbox escape does not start
next to the payments data.

## 2. Module boundaries

| Module | Owns | Publishes | Consumes |
|---|---|---|---|
| `accounts` | users, profiles, OTP, sessions | `UserRegistered` | none |
| `rbac` | groups, object capabilities | none | `UserRegistered` |
| `catalog` | tracks, courses, chapters, lessons, progress | `LessonCompleted` | `PaymentSucceeded` |
| `content` | MDX compile, lint, cached HTML | `ContentPublished` | none |
| `exercises` | quiz/code/sql problems, tests, hints | `ExerciseSolved` | none |
| `submissions` | submissions, test results | `SubmissionJudged` | `ExerciseSolved` |
| `judge_gateway` | job publish, result intake | `SubmissionQueued` | `SubmissionJudged` |
| `contests` | contests, participation, clarifications, scoreboard | `ContestFinished` | `SubmissionJudged` |
| `rating` | Glicko-2 state and history | `RatingUpdated` | `ContestFinished` |
| `gamification` | XP, streaks, badges, weekly board | `XpAwarded` | multiple |
| `community` | comments, forum, votes | none | none |
| `commerce` | orders, payments, discounts, enrollments | `PaymentSucceeded` | none |
| `certificates` | issuance, verification | none | `CourseCompleted` |

Rules:

1. No cross-module model imports. Import the *service* (`commerce.services.enroll`) or
   subscribe to an event.
2. Every event is dispatched after commit (`transaction.on_commit`) so subscribers never
   see uncommitted rows.
3. Read models that must join modules belong to the module that renders them and query by
   ID list.

## 3. Submission judging

```mermaid
sequenceDiagram
  autonumber
  participant U as Browser
  participant API as Django API
  participant DB as PostgreSQL
  participant MQ as RabbitMQ
  participant W as Judge worker
  participant G as go-judge
  participant R as Redis

  U->>API: POST /submissions (Idempotency-Key)
  API->>API: auth, rate limit, language/size validation
  API->>DB: INSERT submission status QUEUED
  API->>MQ: publish judge.job.v1 on_commit
  API-->>U: 202 id, status_url, stream_url
  MQ->>W: deliver (acks_late, prefetch 1)
  W->>DB: status RUNNING
  W->>R: PUBLISH submission id status RUNNING
  W->>W: fetch test cases (S3, sha256 cache)
  W->>G: compile once
  loop each test
    W->>G: run with limits
    G-->>W: verdict, time, memory
    W->>R: PUBLISH test progress
  end
  W->>DB: UPDATE submission verdict, score, judged_at
  W->>MQ: ack
  W->>R: PUBLISH status FINISHED
  API-->>U: SSE event stream
```

Priority queues are ordered `judge.contest`, `judge.practice`, `judge.custom_run`,
`judge.rejudge`, each with a DLQ. Retries happen only for infrastructure faults (`SE`),
never for a wrong answer. Judging is idempotent: the same `submission_id` delivered twice
writes the same terminal state, and the second write is a no-op guarded by
`status != FINISHED`.

Scoreboard and submission status use Redis Pub/Sub. The API's SSE endpoint subscribes per
connection, so a 200-person contest costs 200 subscriptions on one process. That is
acceptable at this scale; a shared subscriber with fan-out is the documented upgrade path.

## 4. Contest scoring

```mermaid
sequenceDiagram
  participant C as Contestant
  participant API
  participant MQ
  participant W as Judge
  participant SC as Scoreboard (Redis ZSET)
  participant RT as Rating task

  C->>API: submit contest problem
  API->>MQ: judge.job.v1 queue judge.contest
  W->>API: result callback
  API->>API: validate participation window (personal_start for virtual)
  alt before freeze_at or own submission
    API->>SC: ZADD scoreboard
    API->>SC: PUBLISH scoreboard contest
  else frozen
    API->>API: store real score, hide from public board
  end
  Note over API: contest end
  API->>API: ContestFinished event
  API->>RT: rate_contest contest_id
  RT->>RT: Glicko-2 batch over participants
  RT->>SC: unfreeze, publish final
```

ACM scoring is `(solved, penalty)` where penalty is minutes to accepted plus 20 per
rejected attempt on problems that were eventually accepted. IOI scoring takes the max
subtask score per problem. Freeze hides the public board only; contestants always see
their own verdicts.

## 5. Payment

```mermaid
sequenceDiagram
  participant U as User
  participant API
  participant ZP as Zarinpal
  participant DB
  participant CB as Callback

  U->>API: POST /orders course_id, discount_code
  API->>DB: create Order PENDING with price snapshot
  U->>API: POST /payments order_id, idempotency_key
  API->>ZP: payment request (amount, callback, description)
  ZP-->>API: authority
  API->>DB: Payment PENDING with authority
  API-->>U: redirect URL
  U->>ZP: pays
  ZP->>CB: GET callback with Authority and Status
  CB->>ZP: verify server-side (amount + authority)
  CB->>DB: Payment PAID with ref_id, idempotent on authority
  CB->>DB: Order PAID, Enrollment created
  CB-->>U: redirect to order page
```

Never trust the callback query string. Amount is re-checked against the stored order; a
mismatch is logged, the payment is marked `SUSPICIOUS`, and no enrollment is created. The
callback is idempotent on `authority`, so double delivery yields one enrollment.

## 6. OTP login

```mermaid
sequenceDiagram
  participant U as User
  participant API
  participant Redis
  participant DB
  participant KV as Kavenegar

  U->>API: POST /auth/otp/request phone
  API->>Redis: cooldown and budget checks
  API->>DB: insert OtpRequest code_hash, expires_at +120s
  API->>KV: verify/lookup (template + token)
  API-->>U: 204 always, even for unknown numbers
  U->>API: POST /auth/otp/verify phone, code
  API->>DB: SELECT FOR UPDATE latest unconsumed
  alt hash mismatch
    API->>DB: attempts +1 (committed even on failure)
    API-->>U: 400 otp_invalid or 429 otp_locked
  else valid
    API->>DB: consumed_at = now
    API->>DB: get_or_create user, assign student group
    API-->>U: access JWT plus refresh cookie
  end
```

Failure responses are constant-shaped: whether the phone exists never changes the answer.
Failures commit their attempt counter; raising inside the transaction would roll it back
and give unlimited guesses.

## 7. Frontend rendering

- Public course, lesson-preview, and problem pages: SSR with `revalidate` (60s) and
  `generateMetadata` for OpenGraph. Paid lesson bodies are fetched with the user's
  session and never cached publicly.
- Auth-aware shells (`/dashboard`, `/learn/...`) are dynamic. The access token lives in an
  httpOnly cookie, so the browser cannot read it and server components proxy through
  Next's `cookies()`.
- Code editor, scoreboard, and live results are client components; everything else is
  server-rendered so the RTL layout is stable on first paint.
- No external CDN. Vazirmatn and JetBrains Mono are self-hosted through `next/font/local`.

## 8. Threat model summary

| Surface | Main risk | Mitigation |
|---|---|---|
| Sandbox | escape, fork bomb, network egress | namespaces + cgroups, no NIC, read-only root, tmpfs, go-judge seccomp |
| SQL judge | reading app data, DoS | separate instance, restricted role, statement_timeout, no extensions |
| Payments | forged callback, replay | server-side verify, amount check, idempotent authority |
| Auth | credential stuffing, token theft | throttles, Argon2, rotation with family revocation, CSRF double-submit |
| Content | XSS via MDX | allow-listed components, no raw HTML or script, server-side sanitize |
| Paid content | paywall bypass | authorization in the service layer; bodies never serialized for non-buyers |
