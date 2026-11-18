# Gap Analysis — repo vs. `docs/MASTER_PROMPT.md`

Baseline: `docs/task-0-gap-analysis`, branched from `Alireza-Phase2` (`8b6e946`).
Status reads as of this commit. `Not verified` means the check was not run, not that it passed.

## 1. Coverage (§1–§13)

| Item | Status | Evidence | Note |
|---|---|---|---|
| §1 Educational model, audience, domains | Partial | `docs/design.md`, `README.md` | Positioning documented; no catalog data yet. |
| §1 Freemium + discount codes | Missing | — | No `commerce` app or models. |
| §1 Roles student/creator/admin | Done | `backend/apps/rbac/models.py`, `apps/accounts/api.py:142` | Groups created on signup. |
| §1 Contest Supervisor as grantable permission | Partial | `backend/apps/rbac/models.py` | `supervise` capability exists; no contest target. |
| §2 Track → Course → Chapter → Lesson | Missing | `docs/erd.md` (planned) | Models not implemented. |
| §2 MDX lessons with custom components | Missing | — | No MDX pipeline; `html-react-parser` only. |
| §2 Quiz exercises (4 kinds) | Missing | `docs/erd.md` (planned) | No `exercises` app. |
| §2 Code judge, 5 languages, subtasks | Missing | `judge/README.md` (placeholder) | Contract drafted, worker absent. |
| §2 SQL judge | Partial | `infra/sql-judge/init/01-restricted-role.sql` | Restricted role + compose service exist; no runner. |
| §2 Contests (ACM/IOI, virtual, freeze) | Missing | — | Not started. |
| §2 Glicko-2 batch rating | Missing | — | Not started. |
| §2 Gamification | Missing | — | Not started. |
| §2 Community (comments, forum) | Missing | — | Not started. |
| §2 Hints with XP cost | Missing | — | Not started. |
| §2 Certificates + verification | Missing | — | Not started. |
| §2 Zarinpal payments | Missing | — | No adapter or `PaymentGateway` interface. |
| §2 SMS OTP via Kavenegar | Done | `backend/apps/accounts/services/sms.py` | Adapter protocol + console/memory/Kavenegar. |
| §2 Email/password auth | Partial | `backend/apps/accounts/api.py:174` | Password login exists; no email identifier or registration. |
| §3 Modular monolith + separate judge | Partial | `docs/design.md`, `infra/docker-compose.judge.yml` | Docs and compose split done; only 3 apps exist. |
| §3 Bounded apps (`catalog`…`analytics_events`) | Partial | `backend/apps/` | `accounts`, `rbac`, `common` only; 12 listed apps missing. |
| §3 Service functions / domain events | Partial | `backend/apps/accounts/signals.py` | `post_save` used; no event bus or domain events. |
| §4 Django 5 + Ninja | Done | `backend/requirements.txt` | Django 5.2.18, Ninja 1.7.3. |
| §4 Celery + RabbitMQ + beat | Partial | `backend/config/celery.py`, `config/settings/base.py:167` | Queues declared, DLQ absent, no tasks. |
| §4 PostgreSQL 16 / Redis 7 | Done | `infra/docker-compose.dev.yml` | Both wired; Redis used for cache + rate limit. |
| §4 SSE transport | Missing | `docs/api.md` (planned) | No streaming endpoint. |
| §4 Next.js App Router + TS + Tailwind | Done | `frontend/package.json` | Next 16, TS strict, Tailwind 3.4. |
| §4 shadcn/ui, TanStack Query, CodeMirror | Missing | — | None installed. |
| §4 go-judge | Missing | `infra/docker-compose.judge.yml` | Service declared; no integration code. |
| §4 S3 in prod / MinIO in dev | Partial | `infra/docker-compose.dev.yml`, `.env.example` | MinIO runs; no `boto3` or S3 client in code. |
| §4 ArvanCloud VOD | Missing | — | `video_id` field not implemented. |
| §4 JWT + refresh rotation/revocation | Done | `apps/accounts/services/tokens.py`, `apps/accounts/models.py` | Family revocation tested. |
| §4 Observability (GlitchTip/Prometheus/Grafana/Loki) | Missing | `infra/docker-compose.app.yml` | Only JSON logging; no sentry SDK, metrics, dashboards. |
| §4 Docker Compose on 2 VMs + Traefik | Partial | `infra/docker-compose.*.yml`, `infra/traefik/` | Compose and Traefik done; no monitoring stack. |
| §5 `accounts` models | Done | `apps/accounts/models.py` | `User`, `Profile`, `OtpRequest` + `RefreshSession`. |
| §5 `rbac` / `ContestStaff` | Partial | `apps/rbac/models.py` | Generic grant OK; `ContestStaff` table missing. |
| §5 `catalog`, `exercises`, `submissions` models | Missing | `docs/erd.md` (planned) | Not implemented. |
| §5 `CustomRun`, `QuizAnswerKey`, `AcceptedAnswer`, `Tag`, `Notification`, `WeeklyLeaderboardSnapshot` | Missing | `docs/erd.md` | Absent from ERD and code. |
| §5 UUID public IDs, timestamps | Done | `apps/common/models.py` | `UUIDModel`, `TimeStampedModel`. |
| §5 `TestRunResult` truncation, sample-only output | Missing | — | Not implemented. |
| §6 Submission flow + `on_commit` publish | Missing | — | No submissions app. |
| §6 Priority queues + DLQ | Partial | `config/settings/base.py:172` | 4 queues declared; no DLQ or retry policy. |
| §6 Verdict set | Missing | `docs/contracts/judge-job.v1.md` | Documented only. |
| §6 Sandbox limits + abuse tests | Partial | `infra/docker-compose.judge.yml` | Compose flags only; no tests. |
| §6 SQL judge DB-per-submission, restricted role | Partial | `infra/sql-judge/init/01-restricted-role.sql` | Role policy present; runner missing. |
| §7 `/api/v1`, OpenAPI, typed TS client | Partial | `backend/config/api.py`, `frontend/package.json` | OpenAPI live; `api:types` script exists, no generated schema file. |
| §7 Error envelope `{code,message,details}` | Done | `backend/apps/common/errors.py` | Plus `request_id`. |
| §7 Cursor pagination | Partial | `backend/apps/common/pagination.py` | Helper only; no list endpoint uses it. |
| §7 Rate limits | Partial | `backend/apps/common/ratelimit.py` | OTP/login done; submissions/custom runs deferred. |
| §7 Idempotency keys | Missing | `docs/api.md` (planned) | No submission/payment endpoints. |
| §7 SSE endpoints | Missing | `docs/api.md` (planned) | Not implemented. |
| §8 Quiz form UI, navigator, autosave | Missing | — | No quiz UI. |
| §8 MDX linter + live preview | Missing | — | No author panel. |
| §8 Course sidebar, progress, ToC | Missing | — | No course pages. |
| §8 Inline results, custom input, shortcuts | Missing | — | No problem page. |
| §8 Light/dark defaulting to OS | Done | `frontend/src/components/theme-script.tsx`, `globals.css` | No flash; toggle present. |
| §8 Vazirmatn + JetBrains Mono self-hosted | Done | `frontend/src/app/globals.css` | `@fontsource`, no CDN. |
| §8 i18n + RTL via logical properties | Partial | `frontend/messages/fa.json`, `tailwind.config.ts` | Shell done; 21 backend error codes lack Persian strings. |
| §8 Code/terminal/math LTR | Partial | `frontend/src/app/login/login-form.tsx:181` | `.ltr` utility used in 2 places; no editor yet. |
| §8 Responsive + mobile hint + manifest | Partial | `frontend/public/manifest.json` | Manifest only; no exercise layout. |
| §8 SEO: SSR, sitemap, OG | Partial | `frontend/src/app/layout.tsx:10` | Metadata exists; no sitemap or public content pages. |
| §8 Accessibility WCAG AA | Partial | `frontend/src/app/globals.css:10` | Contrast pairs documented; not audited. |
| §9 CSRF, CORS, CSP | Partial | `backend/config/settings/base.py:128`, `infra/traefik/dynamic.yml` | CSRF double-submit + CORS done; CSP allows `unsafe-inline`. |
| §9 OTP hashing, expiry, throttles | Done | `apps/accounts/services/otp.py`, `api.md` | Attempts commit on failure. |
| §9 Argon2 + rotation/reuse detection | Done | `config/settings/base.py:108`, `tests/test_auth.py` | Tested. |
| §9 Paid content server-side | Missing | — | No paywall yet. |
| §9 Payment verify + audit log | Missing | — | No payments. |
| §9 Plagiarism normalized hash hook | Missing | — | Not started. |
| §9 Backup + restore drill | Partial | `infra/docker-compose.app.yml` | `backups` volume only; no dump job or drill. |
| §10 Two-server split | Partial | `infra/docker-compose.{app,judge}.yml` | Compose split correct; app server runs `judge.rejudge`. |
| §10 Health checks, restart, limits | Partial | `infra/docker-compose.*.yml` | Mostly present; `celery-beat` has no restart/limits. |
| §10 CI/CD + private registry + rollback | Done | `.github/workflows/{ci,deploy}.yml` | Health-check rollback implemented. |
| §10 Mirrors, no foreign CDN | Partial | `infra/mirrors/`, `*/Dockerfile` | Mirror configs exist; Dockerfiles default to upstream registries. |
| §10 One-command dev + seed data | Partial | `infra/docker-compose.dev.yml` | Up works; no go-judge service; seed is users only. |
| §11 GlitchTip | Missing | `.env.example` | `GLITCHTIP_DSN` unused. |
| §11 Structured JSON logs → Loki | Partial | `backend/apps/common/logging.py` | JSON formatter; no shipper. |
| §11 Prometheus metrics + Grafana alerts | Missing | — | Not started. |
| §12 Contracts in `/docs/contracts` | Done | `docs/contracts/judge-job.v1.md` | Job + result + SQL variant. |
| §13 weeks 1–2 scope | Partial | see §2 below | Auth/RBAC/i18n/themes done; CI/mirrors partial. |
| §13 weeks 3–12 scope | Missing | — | Not started, as expected. |

## 2. Phase check — §13 weeks 1–2 and §14 Definition of Done

Week 1–2 deliverables: monorepo, Docker Compose, CI/CD, registry + mirrors, auth (OTP +
email), RBAC, design system, i18n/RTL, themes.

| Deliverable | Status | Evidence | Gap |
|---|---|---|---|
| Monorepo layout | Done | `backend/`, `frontend/`, `judge/`, `infra/`, `docs/` | — |
| Docker Compose (dev/app/judge) | Partial | `infra/docker-compose.*.yml` | Dev stack lacks go-judge; `celery-beat` missing `restart`/limits. |
| CI/CD pipelines | Done | `.github/workflows/ci.yml`, `deploy.yml` | `ci.yml` triggers on `main` only, so feature branches get no PR CI. |
| Private registry | Partial | `deploy.yml` | Registry secrets wired; reachability from Iran unverified. |
| Mirrors (pip/npm/Docker) | Partial | `infra/mirrors/*` | Configs exist but Dockerfiles default to `pypi.org` / `registry.npmjs.org`. |
| Auth: OTP | Done | `apps/accounts/services/otp.py`, `tests/test_auth.py` | Kavenegar path untested against the real API. |
| Auth: email/password | Partial | `apps/accounts/api.py:174` | Phone+password only; no email login or registration. |
| Auth: JWT rotation | Done | `apps/accounts/services/tokens.py` | Store not Redis-backed; DB table used instead. |
| RBAC | Partial | `apps/rbac/` | Roles + generic grants done; contest target returns `503`; no object-level tests beyond grants. |
| Design system | Partial | `frontend/src/app/globals.css`, `components/` | Tokens/header/theme only; no shadcn primitives. |
| i18n/RTL | Partial | `frontend/messages/*.json`, `src/i18n/` | `fa`/`en` key parity OK; 21 backend error codes untranslated. |
| Themes | Done | `theme-script.tsx`, `theme-toggle.tsx` | OS default, no flash. |

### Definition of Done (per feature, §14)

| Criterion | Status | Evidence | Gap |
|---|---|---|---|
| Typed API | Partial | `backend/config/api.py` | Ninja schemas exist; no generated TS client checked in. |
| Tests passing in CI | Partial | `tests/`, `ci.yml` | 59 backend + 24 frontend tests pass locally; no frontend coverage for pages. |
| Persian i18n strings | Partial | `messages/fa.json` | 21 of 33 backend error codes missing. |
| RTL/LTR correct | Partial | `layout.tsx:33` | Shell OK; no exercise/editor layout to verify. |
| Dark/light correct | Done | `globals.css`, `theme-*` | Both themes defined. |
| Permissions server-side | Partial | `apps/rbac/permissions.py` | Admin gates tested; creator/object-capability rules untested at API level. |
| Metrics/logs added | Partial | `apps/common/logging.py` | JSON logs + request id only; no metrics, no error tracking. |
| Docs updated | Partial | `docs/` | Docs describe planned phases as if designed; no gap doc until now. |

### Definition-of-Done gaps by area

- **Tests:** no abuse tests for the sandbox/SQL judge (nothing to test yet), no SSE or
  submission flow tests, no frontend page-level tests, no CSP header assertions.
- **Persian strings:** `csrf_failed`, `forbidden`, `handle_taken`, `internal_error`,
  `invalid_capability`, `invalid_purpose`, `invalid_role`, `invalid_target`, `not_found`,
  `refresh_expired`, `refresh_invalid`, `refresh_missing`, `refresh_reused`,
  `session_revoked`, `target_not_found`, `target_not_installed`, `token_expired`,
  `token_invalid`, `user_not_found`, `weak_password`, `wrong_password`.
- **RTL/dark mode:** no content or exercise surfaces exist, so their DoD is unprovable.
- **Server-side permissions:** `can_edit_track`/`has_capability` have no call sites yet.
- **Logs/metrics:** no Prometheus instrument, no GlitchTip SDK, no queue-depth gauge.
- **Docs:** `docs/design.md` §3 contradicts judge isolation (see §3 below).

## 3. Conflicts between existing docs/code and the master prompt

| # | Existing text | Prompt says | Verdict |
|---|---|---|---|
| C1 | `docs/design.md` §3: `W->>DB: status RUNNING` and `W->>DB: UPDATE submission verdict, score, judged_at` | §3 puts the judge on a "separate VM"; §6 says "The judge server accepts connections **only** from the app server". | **Conflict.** Judge holds DB credentials. Must become an HTTP result callback only. |
| C2 | `docs/contracts/judge-job.v1.md` (Result): "The worker writes the terminal state to the database and publishes this envelope…" | §6.4: "Results are written back via the internal API/DB". | **Ambiguous in the prompt, resolved by your decision** (§4 A1). Contract text must drop the DB write. |
| C3 | `infra/docker-compose.app.yml:126`: `celery -A config worker -Q default,judge.rejudge` | §10: judge workers live on Server 2 only. | **Conflict.** App server consumes a judge queue; rejudge traffic would run on the app host. |
| C4 | `infra/docker-compose.judge.yml`: `env_file: .env`, `DJANGO_SETTINGS_MODULE: config.settings.prod` | §6/§10: judge needs no app-DB access. | **Conflict.** A prod settings file implies `DATABASE_URL`; the judge image would carry app DB config. |
| C5 | `frontend/tsconfig.tsbuildinfo` is tracked (`git ls-files`) | Nothing in the prompt; contradicts `.gitignore` intent. | **Resolved in `8483a2e`, `b8c6e4d`** (was: Generated build artifact in git; 45 `.pyc` files likewise tracked.) |
| C6 | `docs/repository.md` §Branching: "Trunk-based: `main` is always deployable… `feat/<scope>`…" | §13/§14 assume phase work; no branching model specified. | **Resolved except manual GitHub setting.** Branching section updated, `docs/branch-protection.md` added; required checks on `main` are Not verified (applied manually). |
| C7 | `.github/workflows/ci.yml:32`: `python-version: "3.12"` | §4: Python 3.12. | **Resolved in `da46e87`** (`.python-version` + uv/venv docs; was: aligned in CI, conflicts with the host: `python3.12` is absent from `PATH` (only 3.14.4; 3.12 lives in `backend/.venv`).) |
| C8 | `docs/design.md` §3: "The API's SSE endpoint subscribes per connection, so a 200-person contest costs 200 subscriptions on one process." | §4/§8 require SSE; no fan-out limit given. | **Risk, not conflict.** Documented upgrade path exists; fine at <1,000 users. |
| C9 | `docs/erd.md`: `USER }o-o GROUP : member` plus `OBJECT_PERMISSION` | §1: "Django groups + object-level permissions (`django-guardian` or a simple custom `ContestStaff` table)". | **Divergence.** Custom generic grant instead of guardian — acceptable, but `ContestStaff` is absent. |
| C10 | `infra/docker-compose.dev.yml`: no `go-judge` service; `seed_dev` creates users only | §10: "a single `docker compose up` brings up everything, including MinIO and **go-judge**" + seed data incl. problems and a contest. | **Conflict.** Dev stack is incomplete and seed data is narrower than required. |
| C11 | `backend/Dockerfile:15`: `ARG PIP_INDEX_URL=https://pypi.org/simple`; `frontend/Dockerfile:4`: `ARG NPM_CONFIG_REGISTRY=https://registry.npmjs.org` | §10: "use **mirrors** … no external CDNs … at runtime". | **Resolved.** Dockerfile defaults are mirrors; the `images` job passes upstream URLs as build args. |

## 4. Decisions taken as assumptions

**A1 — Judge has no main-DB credentials; results arrive via internal HTTP with a shared
secret.** Agreed. This matches §6's "accepts connections only from the app server" and
makes C1–C4 resolvable. Two notes:

- HMAC alone authenticates the caller but not the payload's freshness. Sign the timestamp
  and reject skew > 5 min, otherwise a captured body can be replayed. The contract already
  has `X-Judge-Signature`; add a timestamp header rather than inventing a new scheme.
- Idempotency must move to the receiver: the API must no-op on a duplicate `submission_id`
  / `job_id`, since the worker can no longer guard with `status != FINISHED` at the DB.

**A2 — No new parallel design docs; existing docs are updated in place.** Agreed, with one
caveat: `docs/design.md` §3/§4 and `docs/contracts/judge-job.v1.md` both describe the
direct-DB write. Updating one without the other leaves the contract lying to the worker
author. Treat them as one change set (T5 below), not two.

### Points where I would push back, or that need your ruling

| # | Topic | Concern | Proposal |
|---|---|---|---|
| Q1 | §6 says results go "via the internal API/DB" | The "/DB" alternative is exactly C1. Two readings in one sentence. | Delete "/DB" from §6 when docs are revised; A1 is the only reading. |
| Q2 | `django-guardian` vs custom grants | §1 offers a choice; repo already picked custom generic grants. Fine, but `ContestStaff` is still required by §5. | Keep custom grants; add `ContestStaff` as a thin model over `ObjectPermission`, or accept `ObjectPermission` alone and amend §5. |
| Q3 | Email/password vs phone-only | `User.phone` is unique and required; `email` nullable. §2 wants email/password login, but the login API takes `phone`. | Decide whether "email login" means email+password or just password-on-phone. Affects `User` constraints. |
| Q5 | CSP `script-src 'unsafe-inline'` | §9 asks for CSP; Next's inline bootstrap usually forces this. Weakening CSP to pass the build is a security decision, not a detail. | Use nonces via middleware before beta; record the exception until then. |
| Q6 | Rate-limit helper swallows cache outages (`return limit`) | Fails open. For OTP this is a brute-force window. | Fail closed for OTP/verify, open for read-only scopes. |
| Q7 | Trunk-based vs phase branches | Repo history uses `Alireza-PhaseN` long-lived branches, contradicting `repository.md`. | Pick one and delete the other; recommend the documented trunk-based flow. |

## 5. Proposed task list (ordered, one branch each)

Payment state machine to be defined in weeks 10–11.

| # | Branch | Scope | Fixes |
|---|---|---|---|
| T1 | `chore/repo-cleanup` | Remove 45 tracked `.pyc` files; untrack `frontend/tsconfig.tsbuildinfo`; add `.pytest_cache/`, `tsbuildinfo` to ignores; document/automate Python 3.12 (uv or `.python-version`) so `python3.12` is not required on PATH. | C5, C7 — done (`8483a2e`, `b8c6e4d`, `da46e87`) |
| T2 | `ci/pr-and-branch-protection` | Make CI a required check via branch protection (`ci.yml` already triggers on `pull_request`); add `docs/*` to the branch convention. | C6 — done (branch protection itself: Not verified) |
| T3 | `chore/mirror-defaults` | Make mirror URLs the Dockerfile defaults (build args stay overridable). | C11 — done |
| T4 | `chore/dev-stack-parity` | Add `go-judge` to the dev compose; extend `seed_dev` with a track, course, quiz, code and SQL problem, one contest. | C10 |
| T5 | `docs/judge-isolation` | Update `design.md` §3/§4 and `contracts/judge-job.v1.md` to remove the DB write; add the timestamped HMAC and receiver-side idempotency. One change set. | C1–C4, A1, Q1 |
| T6 | `fix/judge-compose-creds` | Drop `config.settings.prod` and `DATABASE_URL` from the judge compose; pass only `API_CALLBACK_URL` + `JUDGE_SHARED_SECRET`; remove `judge.rejudge` from the app-server worker. | C3, C4 |
| T13 | `fix/ratelimit-fail-closed` | OTP request/verify and login fail closed on cache outage; read-only scopes may fail open; tests for both paths. | Q6 |
| T8 | `feat/i18n-error-codes` | Add the 21 missing Persian error strings; add a test asserting `fa` covers every backend `ApiError` code. | DoD i18n |
| T11 | `chore/api-client-generation` | Generate `api-schema.d.ts` in CI and fail on drift. | DoD typed API |
| T12 | `docs/erd-sync` | Add `CustomRun`, `QuizAnswerKey`, `Tag`, `Notification`, `WeeklyLeaderboardSnapshot`, payment audit table to `erd.md`. | §5 gaps |
| T9 | `feat/observability-baseline` | GlitchTip SDK, Prometheus `/metrics`, queue-depth gauge, Loki-ready log config. | §11, DoD metrics |
| T10 | `feat/auth-email` | Email+password as a second login method, consistent with §5 nullable email/password. | Q3 |

**Deferred**

| Item | When | Note |
|---|---|---|
| T7 ContestStaff / contest target (`feat/rbac-contest-target`) | Weeks 8–10 | Lands with the `contests` app; fixes C9. |
| CSP nonce (replace `script-src 'unsafe-inline'`) | Before closed beta | `unsafe-inline` recorded as an accepted exception until then. |
| Payment state machine | Weeks 10–11 | Defined with `commerce`. |

Then resume §13 from week 3 (catalog + MDX).

## 6. Accepted decisions

| Ref | Decision | Follow-up |
|---|---|---|
| A1 | Judge has no main-DB credentials; results only via internal HTTP API with a shared secret. | T5, T6 |
| A2 | No new parallel design docs; existing docs are updated in place. | T5, T12 |
| Q1 | Remove "/DB" from `docs/MASTER_PROMPT.md` §6.4 ("via the internal API/DB" becomes "via the internal API"). | Applied in a separate commit. |
| Q2 | Keep custom grants (`ObjectPermission`) rather than `django-guardian`. | `ContestStaff` deferred (T7, weeks 8–10). |
| Q3 | Email+password is added as a second login method; phone OTP stays primary. | T10 |
| Q5 | CSP nonce before closed beta; `unsafe-inline` is an accepted exception until then. | Deferred. |
| Q6 | OTP request/verify and login fail closed when the cache is down; read-only scopes may fail open. | T13 |
| Q7 | Trunk-based flow as documented in `docs/repository.md`; `Alireza-PhaseN` long-lived branches are not the model going forward. | T2 |
