# Repository Layout & Conventions

```text
.
├── backend/                 Django 5 + Ninja monolith
│   ├── config/              settings (base/dev/test/prod), urls, api, celery
│   ├── apps/
│   │   ├── common/          base models, errors, rate limit, middleware
│   │   ├── accounts/        users, OTP, sessions, profile
│   │   └── rbac/            groups + object capabilities
│   └── tests/               pytest suites (unit + integration/security marks)
├── frontend/                Next.js App Router + TypeScript
├── judge/                   placeholder for the Celery worker image (weeks 5-8)
├── infra/
│   ├── docker-compose.dev.yml
│   ├── docker-compose.app.yml
│   ├── docker-compose.judge.yml
│   ├── traefik/
│   └── mirrors/             pip / npm / docker registry config for Iran
├── docs/                    design, ERD, API, message contracts
└── .github/workflows/       ci.yml, deploy.yml
```

## Backend conventions

- Python 3.12 in Docker; local tooling uses `uv` with `backend/requirements.txt` as the
  single source of truth.
- Formatting: `ruff format`; linting: `ruff check` (E, F, I, B, UP, DJ rules).
- Types: Pydantic schemas at the API boundary. Domain functions take IDs and return
  models; no schema objects leak into services.
- Every view is thin: parse, authorize, call a service, serialize.
- New endpoints need: schema, test, Persian string keys (added to both locale files), and
  a rate limit if unauthenticated or expensive.

## Frontend conventions

- TypeScript strict. No `any` at module boundaries; use the generated API client.
- All user-facing copy through `next-intl` message files (`fa.json` now, `en.json` mirror
  for structure). No literal Persian strings in components.
- Tailwind logical utilities only (`ms-*`, `me-*`, `start-*`, `end-*`), never `ml-*` for
  layout that must mirror.
- Code, terminal output, and math render `dir="ltr"`.

## Branching & commits

- Trunk-based: `main` is always deployable; work happens on short-lived
  `feat/<scope>`, `fix/<scope>`, `chore/<scope>` branches merged by squash.
- Commit subjects use Conventional Commits (`feat(auth): rotate refresh tokens`). The
  squash title becomes the changelog entry.
- PR must pass `ci.yml` (lint, types, tests, build) and one peer review. Security-relevant
  PRs (judge, payments, auth) need a second reviewer.

## Definition of done

Typed schema, tests (including abuse cases where relevant), Persian i18n keys, RTL and
theme checked, permissions enforced server-side, metrics/logs emitted, docs updated.
