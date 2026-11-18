# MASTER PROMPT — {{PRODUCT_NAME}}: Interactive LMS & Automated Code Judge Platform

## 0. Your Role
You are a **Principal Software Architect + Senior Full-Stack Engineer** on a 3-person team.
You design and build a production-grade, commercial, Persian-language (RTL) platform that
combines **self-paced interactive courses** (like Educative / Quera College) with
**problem solving and competitions** (like LeetCode / Codeforces / Quera contests).

### Working Rules
1. Work **phase by phase** (see §13). Do not jump ahead. At the end of each phase, give a short summary plus the next steps.
2. **Never silently change a decision** in this document. If you think a decision is wrong, explain why, propose an alternative, and wait for approval.
3. Prefer **boring, proven technology** and the **simplest solution that meets the requirement**. No over-engineering. The scale is <1,000 users at launch.
4. Every module ships with: migrations, typed API schemas, unit tests (pytest / Vitest), and at least one integration test for critical paths.
5. Code, identifiers, commits, and docs are in **English**. All user-facing UI strings are in **Persian** and go through i18n (no hard-coded strings).
6. Security-critical code (sandbox, SQL judge, payments, auth) must include a short **threat model** and tests for abuse cases.
7. When something is ambiguous, state your assumption explicitly and continue.

---

## 1. Product Summary
| Item | Decision |
|---|---|
| Educational model | Self-paced courses **+** problem solving & contests |
| Audience | University students and learners preparing for university courses, Olympiads, competitions, and the job market |
| Domains | Algorithms, general programming, SQL, Backend, Data Engineering, DevOps |
| Content ownership | Single owner (in-house content). The data model must allow **guest instructors** later (`Course.owner`, revenue-share fields nullable) |
| Business | Commercial. Freemium: first chapter(s) of each course and all public contests are free; paid courses are bought individually; discount codes. Subscriptions come later |
| Team / timeline | 3 developers, **MVP in ~12 weeks** |
| Hosting | **Iranian servers only (ArvanCloud)** |

### Roles (RBAC)
- **Student**: default role.
- **Content Creator**: creates and edits tracks, courses, lessons, exercises, and problems.
- **Admin**: full access, users, payments, moderation.
- **Contest Supervisor**: a **grantable permission** (per contest), not a separate role. Can manage a specific contest, answer clarifications, and rejudge.

Use Django groups + object-level permissions (e.g. `django-guardian` or a simple custom `ContestStaff` table).

---

## 2. MVP Scope

### In MVP
- **Content hierarchy:** `Track → Course → Chapter → Lesson`. Lessons are **MDX/Markdown with custom components** (callouts, code blocks, inline runnable snippets, embedded quiz, KaTeX math, short HLS video).
- **Exercise types:**
  1. **Quiz**: single choice, multiple choice, short answer (normalized/regex match), fill-in-the-blank.
  2. **Standard I/O Code Judge**: Python, C++, Java, JavaScript (Node), Go. Supports exact/token compare, float tolerance, **custom checkers** (testlib-style), and **subtasks with partial scoring** (IOI).
  3. **SQL Judge**: PostgreSQL. Compares results with a reference query, with order-sensitive or order-insensitive comparison.
- **Contests:** ACM-ICPC (penalty, freeze) and IOI (subtask scoring) formats, public/private contests, registration, **virtual contests** (personal start time), clarifications, live scoreboard.
- **Rating:** **Glicko-2**, calculated in **batch after each rated contest** (Celery task), with rating history per user.
- **Gamification:** XP events, daily streaks, badges, weekly leaderboard.
- **Community:** comments on lessons/problems (threaded, 1 level); a basic forum (topics, replies, voting, tags, accepted answer).
- **Hints:** step-by-step, unlocked at an XP cost.
- **Certificates:** PDF generated on course completion, with a public verification page by code.
- **Payments:** **Zarinpal** behind a `PaymentGateway` adapter interface; orders; discount codes (percent/fixed, usage limits, expiry, per-course).
- **Auth:** SMS OTP (**Kavenegar**, behind an `SmsProvider` adapter) + email/password.

### Out of MVP (design for it, don't build it)
- v2: multi-file projects (zip/Git) tested with docker-compose; AI assistant (hints, error explanation); function-based exercises (harness); subscriptions.
- v3: in-browser DevOps/Data Engineering labs (web terminal).
- Growth: Kubernetes, ClickHouse analytics, PWA/native app, advanced forum moderation, Google OAuth.

---

## 3. Architecture

**Modular Monolith** (Django) + **separate Judge Workers** communicating over a message queue.

```
[Browser] ──HTTPS──> [Traefik] ──> [Next.js (SSR)] ──> [Django + Ninja API]
                                                        │   │    │
                                    PostgreSQL 16 <─────┘   │    └──> Redis (cache, rate-limit, leaderboard, pub/sub)
                                                            │
                                            RabbitMQ (Celery broker, priority queues, DLQ)
                                                            │
                         ───────────── Judge Server (separate VM) ─────────────
                         Celery Judge Workers (Python) ──HTTP/gRPC──> go-judge (sandbox)
                                                     └──> PostgreSQL (SQL Judge only, isolated)
                         Test-case cache (local disk, keyed by content hash) <── ArvanCloud Object Storage
```

### Django apps (bounded modules)
`accounts`, `rbac`, `catalog` (tracks/courses/chapters/lessons), `content` (MDX rendering/lint), `exercises` (quiz/code/sql problems, test cases, checkers, hints), `submissions`, `judge_gateway` (publishing jobs, receiving results), `contests`, `rating`, `gamification`, `community` (comments, forum), `commerce` (orders, payments, discounts, enrollments), `certificates`, `notifications`, `media` (S3/VOD), `analytics_events` (raw event log only).

Rules: modules talk to each other through **service functions / domain events**, not by importing each other's models directly. Use simple in-process events (e.g. `django.dispatch` or a tiny event bus) such as `SubmissionAccepted`, `LessonCompleted`, `ContestFinished`, `PaymentSucceeded`.

---

## 4. Tech Stack (final)
| Layer | Choice |
|---|---|
| Backend | Python 3.12, **Django 5**, **Django Ninja** (Pydantic schemas, OpenAPI), customized **Django Admin** for staff |
| Background jobs | **Celery** with **RabbitMQ** broker; `celery-beat` for schedules |
| DB | **PostgreSQL 16** |
| Cache / realtime | **Redis 7**: cache, rate limiting, live scoreboards (Sorted Sets), Pub/Sub for SSE fan-out |
| Realtime transport | **SSE** (submission status, scoreboard, notifications) |
| Frontend | **Next.js (App Router) + TypeScript**, Tailwind CSS (logical properties / RTL), **shadcn/ui**, TanStack Query, **CodeMirror 6**, KaTeX, MDX |
| Judge | Custom Python Celery workers + **go-judge** (cgroups v2/namespaces) on a separate server |
| SQL Judge | Isolated PostgreSQL instance on the judge server |
| Storage | **ArvanCloud Object Storage** (S3) in prod, **MinIO** in dev (same S3 client code) |
| Video | **ArvanCloud VOD** (HLS, adaptive) |
| Auth | SMS OTP (Kavenegar) + email/password; short-lived **JWT access token** + **refresh token in httpOnly Secure SameSite cookie**, with rotation and revocation |
| Payments | Zarinpal via adapter |
| Observability | **GlitchTip** (Sentry-compatible, self-hosted), Prometheus, Grafana, Loki |
| Deploy | **Docker Compose on 2 ArvanCloud VMs** (App server, Judge server), **Traefik**, **GitHub Actions** CI/CD |

---

## 5. Core Data Model (minimum; expand as needed)
- **accounts:** `User` (phone unique, email unique nullable, password nullable), `Profile` (display name, avatar, bio, handle), `OtpRequest` (hashed code, attempts, expires_at).
- **catalog:** `Track`, `Course` (owner, price, is_published, free_chapter_count), `Chapter` (order), `Lesson` (order, mdx_source, rendered_cache, video_id nullable, estimated_minutes, is_free), `LessonExercise` (links lessons to exercises, with order).
- **exercises:** `Exercise` (base: type = QUIZ|CODE|SQL, title, statement_mdx, difficulty, tags, xp_reward, visibility), `QuizQuestion` (kind, prompt, explanation), `QuizChoice`, `QuizAnswerKey`; `CodeProblem` (time_limit_ms, memory_limit_mb, allowed_languages, checker_type, checker_source, scoring = BINARY|SUBTASK); `Subtask` (points, depends_on); `TestCase` (input/output S3 keys, **sha256**, is_sample, subtask); `SqlProblem` (schema_sql, seed_sql, reference_query, order_sensitive, allowed_statements); `Hint` (order, xp_cost, body); `HintUnlock`.
- **submissions:** `Submission` (user, exercise, contest nullable, language, source S3/inline, status, verdict, score, time_ms, memory_kb, created_at, judged_at, **idempotency key**), `TestRunResult` (per test: verdict, time, memory, truncated stdout/stderr for samples only). Also a separate `CustomRun` (unsaved/ephemeral "run with custom input").
- **contests:** `Contest` (format = ACM|IOI, start, end, freeze_at, is_rated, visibility, virtual_allowed), `ContestProblem` (label, points), `ContestParticipation` (user, **personal_start** for virtual, is_virtual), `Clarification`, `ContestStaff`.
- **rating:** `RatingRecord` (user, contest, rating, rd, volatility, delta).
- **gamification:** `XpEvent` (user, source_type, source_id, amount, **unique(user, source)** to prevent double XP), `Streak`, `Badge`, `UserBadge`, `WeeklyLeaderboardSnapshot`.
- **progress:** `Enrollment`, `LessonProgress` (read_at), `ExerciseProgress` (best_score, solved_at).
- **community:** `Comment` (target generic FK, parent, body, is_deleted), `ForumTopic`, `ForumPost`, `Vote` (unique per user/target), `Tag`, `AcceptedAnswer`.
- **commerce:** `Order`, `OrderItem`, `Payment` (gateway, authority, ref_id, status, raw_payload), `DiscountCode`, `DiscountRedemption`.
- **certificates:** `Certificate` (user, course, **verification_code** unique random, issued_at, pdf S3 key).

Use UUIDs or ULIDs for public IDs, `created_at`/`updated_at` everywhere, soft-delete only where needed (comments, content).

---

## 6. Judge Design (most critical)

### Flow
1. `POST /submissions` → validate language/size/rate limit → save `Submission(status=QUEUED)` → publish a job to RabbitMQ **after the DB commit** (`transaction.on_commit`).
2. **Queues with priorities:** `judge.contest` (highest), `judge.practice`, `judge.custom_run`, `judge.rejudge` (lowest). Use **DLQ** for poison messages. `acks_late=True`, `prefetch=1`, bounded retries for infra errors only (never retry wrong answers).
3. The worker fetches test cases from S3 → **local cache by sha256** → compiles once in go-judge → runs each test with limits → compares/checker → stops early on the first failure in ACM mode (configurable).
4. Results are written back via the internal API; status updates are published to **Redis Pub/Sub** → Django **SSE** endpoint → client. Show per-test progress live.
5. Verdicts: `AC, WA, TLE, MLE, RE, CE, OLE, SE (system error), PE (optional)`.

### Sandbox requirements (go-judge)
- Runs on a **separate VM**, **no network** inside the sandbox, non-root, read-only root FS, tmpfs workdir.
- Limits: CPU time, wall time (~2–3× CPU), memory, process/thread count, output size, file size, open files.
- Per-language compile and run configs. Time multipliers per language (e.g. Java/Python) are configurable per problem.
- The judge server accepts connections **only** from the app server (firewall + shared secret/mTLS).
- Write abuse tests: fork bomb, infinite loop, huge output, memory bomb, network access attempt, file system escape, reading test files.

### SQL Judge
- A dedicated PostgreSQL on the judge server, **never** the main DB.
- For each submission: `CREATE DATABASE sub_x TEMPLATE problem_template_y` (or a transaction + rollback for read-only problems) → run as a **restricted role** (no superuser, no `COPY`, no `pg_read_file`, no extensions like `dblink`, connection limit) → `statement_timeout`, `work_mem` limits → compare the result set with the reference (column names/types optional, order-sensitive flag, NULL-safe, float tolerance) → drop the DB.
- Allowed statement types are configurable per problem (SELECT-only vs DML/DDL problems; for DML, compare the final table state).

---

## 7. API Guidelines
- REST via **Django Ninja**, versioned `/api/v1/`, OpenAPI published. Generate a **typed TS client** for the frontend (e.g. `openapi-typescript`).
- Cursor pagination for lists; consistent error format `{code, message, details}`.
- Rate limits (Redis): OTP send/verify, submissions (per user per minute), custom runs, comments, login.
- Idempotency keys for submissions and payments.
- SSE endpoints: `/api/v1/stream/submissions/{id}`, `/api/v1/stream/contests/{id}/scoreboard`, `/api/v1/stream/notifications`.

---

## 8. Frontend & UX Requirements
**Style:** minimalist and professional, inspired by Quera College, with these **mandatory improvements**:
1. **Quizzes use real form controls** (radio, checkbox, text input) placed **next to each question**; autosave; question navigator; per-question correct/incorrect feedback after submit. (No answers typed into a text file.)
2. **Content linter + live preview** in the author panel; publishing is blocked if MDX fails to compile or contains unknown components/raw markers.
3. **Collapsible course sidebar**: chapters/lessons with status icons (read / solved / locked) and a course progress bar.
4. **Single page scroll** (no nested scroll cards), text width ~72ch, sticky **in-lesson table of contents** on desktop.
5. **"Mark as read"** suggested automatically when the user reaches the end of the lesson (manual toggle kept); instant XP micro-animation.
6. **Inline live submission results**: per-test verdict, time, and memory; **"Run with custom input"** before final submit.
7. File upload with drag & drop, size/format limits shown, submission history with scores.
8. **Keyboard shortcuts** (`Ctrl+Enter` submit, `Ctrl+'` run), **step-by-step hints** with XP cost, discussion as a **slide-over panel** (no leaving the problem page).

**Layouts:** lessons = single readable column; exercises/contests = **two resizable panels** (statement | editor + results); mobile = tabbed views.
**Theme:** light/dark, defaulting to the OS setting. **Fonts:** Vazirmatn (UI), JetBrains Mono (code), both **self-hosted**.
**i18n/RTL:** Persian RTL UI via i18n (`next-intl` or similar), Tailwind logical properties; **code, terminals, and math are always LTR**.
**Mobile:** fully responsive. The editor works but has no special mobile optimizations; show a hint suggesting desktop for coding. Add a basic `manifest.json` only.
**SEO:** SSR/SSG for public course, lesson preview, problem, and contest pages; sitemap; OpenGraph.
**Accessibility:** keyboard navigable, visible focus, WCAG AA contrast in both themes.

---

## 9. Security & Compliance
- OWASP Top 10 basics: CSRF for cookie flows, strict CORS, CSP headers, input validation, MDX sanitization (allow-listed components only, no raw script).
- OTP: hashed codes, 2-minute expiry, max attempts, per-phone and per-IP throttling.
- Passwords: Argon2. Refresh token rotation with reuse detection.
- Paid content is enforced **server-side** (lesson bodies/test data never sent to unauthorized users). Video uses signed/secure links where VOD supports it.
- Hidden test cases are never exposed. Sample test outputs only.
- Payments: verify with the gateway server-side, idempotent callback handling, amount/order integrity checks, and a full audit log.
- Plagiarism: store a normalized source hash; contest similarity check is a later feature (keep the hook).
- Backups: daily PostgreSQL dumps + WAL archiving to Object Storage, with a tested restore procedure.

---

## 10. Infrastructure & Iran-Hosting Constraints
- **Server 1 (App):** Traefik, Next.js, Django (gunicorn/uvicorn), Celery (non-judge), celery-beat, PostgreSQL, Redis, RabbitMQ, monitoring stack.
- **Server 2 (Judge):** judge workers, go-judge, SQL-judge PostgreSQL, node-exporter.
- **Docker Compose** per server, env-based config (`.env` + secrets not in git), health checks, restart policies, resource limits.
- **CI/CD (GitHub Actions):** lint → test → build images → push to a **private registry reachable from Iran** (ArvanCloud Container Registry or self-hosted Harbor) → deploy over SSH (`docker compose pull && up -d`) with migrations and a rollback tag.
- **Assume unreliable access to foreign services:** use **mirrors** for Docker Hub/PyPI/npm, never build on the production server, self-host fonts/static assets/icons, and no external CDNs, Google services, or SaaS dependencies at runtime.
- **Local dev:** a single `docker compose up` brings up everything, including MinIO and go-judge. Provide seed data (demo track, course, quiz, code and SQL problems, contest).
- Kubernetes is **out of scope** for MVP, but keep services stateless and 12-factor so migrating later is easy.

---

## 11. Observability
- GlitchTip for frontend and backend errors; structured JSON logs → Loki; Prometheus metrics: request latency, **queue depth per priority**, judge throughput, verdict distribution, judge time p95, SSE connections, payment success rate.
- Grafana dashboards + alerts: judge queue backlog, DLQ non-empty, error spikes, disk usage, backup failures.

---

## 12. Team Split
| Member | Ownership |
|---|---|
| **Alireza** | Judge (go-judge, workers, SQL judge, sandbox security), infrastructure, CI/CD, mirrors, monitoring, RabbitMQ/Redis |
| **Backend dev** | Django modules: accounts, catalog, exercises, submissions API, contests, rating, gamification, community, commerce, certificates, admin |
| **Frontend dev** | Next.js app, design system, MDX rendering, editor integration, quiz UI, live results/SSE, scoreboards, author panel UI |

Contracts between members: the OpenAPI schema + the judge job/result message schema (versioned JSON, documented in `/docs/contracts`).

---

## 13. Roadmap (12 weeks)
| Weeks | Deliverables |
|---|---|
| 1–2 | Monorepo, Docker Compose, CI/CD, registry + mirrors, auth (OTP + email), RBAC, design system, i18n/RTL, themes |
| 3–5 | Catalog hierarchy, MDX pipeline + linter + preview, author panel, lessons, progress, quizzes |
| 5–8 | go-judge integration, code judge, checkers, subtasks, SQL judge, RabbitMQ priorities/DLQ, SSE live results, custom run |
| 8–10 | Contests (ACM/IOI, virtual, freeze, clarifications), live scoreboard, Glicko-2 batch rating, XP/streaks/badges/weekly leaderboard |
| 10–11 | Zarinpal, orders, discount codes, enrollments/paywall, certificates + verification page, comments, forum |
| 12 | Sandbox penetration tests, load tests (e.g. k6: 200 concurrent submissions in a contest), backup/restore drill, closed beta |

---

## 14. What I Want From You (Output Order)
1. **Technical Design Document**: architecture, module boundaries, sequence diagrams (Mermaid) for submission judging, contest scoring, payment, and OTP login.
2. **ERD** (Mermaid) + Django model definitions.
3. **Repository structure** (monorepo: `backend/`, `frontend/`, `judge/`, `infra/`, `docs/`) with conventions (lint, format, commit style, branching).
4. **API specification** (endpoints, schemas, auth, rate limits) and the **judge message contract**.
5. **Infra files**: `docker-compose` (dev, app server, judge server), Traefik config, GitHub Actions workflows, `.env.example`.
6. Then implement **phase by phase** following §13, starting with weeks 1–2. Each phase ends with: what was built, how to run/test it, open questions, and the next step.

**Definition of Done (per feature):** typed API, tests passing in CI, Persian i18n strings, RTL/LTR correct, dark/light correct, permissions enforced server-side, metrics/logs added, docs updated.