# My-LMS

Persian-first (RTL) interactive LMS with an automated code/SQL judge and contests.
Django 5 + Ninja modular monolith, Next.js App Router frontend, separate judge server.

Design docs live in [`docs/`](docs/README.md).

## Quick start (Docker)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.dev.yml up --build
docker compose -f infra/docker-compose.dev.yml exec django python manage.py seed_dev
```

- Web: http://localhost:3000 (the `/api/v1/*` path is proxied to Django)
- API docs: http://localhost:8000/api/v1/docs
- Admin: http://localhost:8000/admin
- RabbitMQ UI: http://localhost:15672 · MinIO: http://localhost:9001

Demo users (password `demo-pass-1234`): `09120000001` admin, `09120000002` creator,
`09120000003` student. In dev, OTP codes print to the `django` container log
(`SMS_PROVIDER=console`).

## Without Docker

```bash
# backend (tests need no external services)
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=config.settings.test pytest
ruff check . && ruff format --check .

# frontend
cd frontend
npm ci
npm run typecheck && npm test && npm run build
```

Inside Iran, use the mirror configs in `infra/mirrors/` (pip, npm, Docker daemon).

## Layout

| Path | Purpose |
|---|---|
| `backend/` | Django apps: `common`, `accounts` (OTP, JWT rotation), `rbac` |
| `frontend/` | Next.js, next-intl (fa default), Tailwind with logical properties, light/dark |
| `judge/` | Judge worker (phase 3) |
| `infra/` | Compose files for dev/app/judge, Traefik, mirrors, SQL-judge role |
| `docs/` | Design, ERD, API, judge message contract |
| `.github/workflows/` | CI (lint, tests, build, images) and SSH deploy with rollback |
