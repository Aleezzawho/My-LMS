# Gap Analysis — repo vs. `docs/MASTER_PROMPT.md`

Baseline: `docs/task-0-gap-analysis`, branched from `Alireza-Phase2` (`4cb461b`).
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
| Tests passing in CI | Partial | `tests/`, `ci.yml` | 51 backend + 24 frontend tests pass locally; no frontend coverage for pages. |
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
| C5 | `frontend/tsconfig.tsbuildinfo` is tracked (`git ls-files`) | Nothing in the prompt; contradicts `.gitignore` intent. | **Repo hygiene conflict.** Generated build artifact in git; 45 `.pyc` files likewise tracked. |
| C6 | `docs/repository.md` §Branching: "Trunk-based: `main` is always deployable… `feat/<scope>`…" | §13/§14 assume phase work; no branching model specified. | **No conflict, but incomplete**: no `docs/*` branch type, and `ci.yml` only runs on `main`, so PR CI never fires. |
| C7 | `.github/workflows/ci.yml:32`: `python-version: "3.12"` | §4: Python 3.12. | **Aligned in CI**, conflicts with the host: `python3.12` is absent from `PATH` (only 3.14.4; 3.12 lives in `backend/.venv`). |
| C8 | `docs/design.md` §3: "The API's SSE endpoint subscribes per connection, so a 200-person contest costs 200 subscriptions on one process." | §4/§8 require SSE; no fan-out limit given. | **Risk, not conflict.** Documented upgrade path exists; fine at <1,000 users. |
| C9 | `docs/erd.md`: `USER }o-o GROUP : member` plus `OBJECT_PERMISSION` | §1: "Django groups + object-level permissions (`django-guardian` or a simple custom `ContestStaff` table)". | **Divergence.** Custom generic grant instead of guardian — acceptable, but `ContestStaff` is absent. |
| C10 | `infra/docker-compose.dev.yml`: no `go-judge` service; `seed_dev` creates users only | §10: "a single `docker compose up` brings up everything, including MinIO and **go-judge**" + seed data incl. problems and a contest. | **Conflict.** Dev stack is incomplete and seed data is narrower than required. |
| C11 | `backend/Dockerfile:15`: `ARG PIP_INDEX_URL=https://pypi.org/simple`; `frontend/Dockerfile:4`: `ARG NPM_CONFIG_REGISTRY=https://registry.npmjs.org` | §10: "use **mirrors** … no external CDNs … at runtime". | **Conflict.** Mirrors exist as files but are not the defaults. |
| C12 | `docs/design.md` §5: payment callback marks `SUSPICIOUS` on amount mismatch | §9: "amount/order integrity checks, and a **full audit log**". | **Partial.** `SUSPICIOUS` state is an invention not in §5's `Payment.status` list; audit log absent from ERD. |
