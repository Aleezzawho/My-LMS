# API v1

Base path `/api/v1`. OpenAPI JSON at `/api/v1/openapi.json`, Swagger UI at `/api/v1/docs`.
The TypeScript client is generated with `openapi-typescript` in `frontend/package.json`
(`npm run api:types`).

## Conventions

- JSON only. `Content-Type: application/json` on mutations.
- Errors always use the same envelope:

```json
{
  "code": "otp_invalid",
  "message": "The code is incorrect or has expired.",
  "details": null,
  "request_id": "9f1c..."
}
```

`code` is stable and machine-readable; `message` is English for developers (the UI
translates `code` into Persian). Validation failures return `422` with `details` as a list
of `{loc, message}`.
- Every response carries `X-Request-ID` (echoed from the request when printable, otherwise
  generated) and `Server-Timing`.
- Timestamps are ISO 8601 with offset (`+03:30` in Tehran).
- Public identifiers are UUIDs. Internal numeric IDs never leave the server.

## Authentication

| Client | Mechanism |
|---|---|
| Browser | httpOnly `lms_access` cookie (15 min) + httpOnly `lms_refresh` (7 days, path `/api/v1/auth`) |
| API/CLI | `Authorization: Bearer <access_token>` |

Mutations authenticated by cookie require the double-submit header
`X-CSRF-Token`, whose value must equal the non-httpOnly `lms_csrf` cookie. Bearer requests
are exempt. Refresh tokens rotate on every use; reusing a rotated token revokes the whole
family and returns `refresh_reused`.

### Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| `POST` | `/auth/otp/request` | none | `{phone, purpose?}` → `204`. Always 204 for valid input, even for unknown phones |
| `POST` | `/auth/otp/verify` | none | `{phone, code, purpose?}` → `TokenOut`; creates the account on first use |
| `POST` | `/auth/login` | none | `{phone, password}` → `TokenOut` |
| `POST` | `/auth/refresh` | refresh cookie | rotates, returns `TokenOut` |
| `POST` | `/auth/logout` | refresh cookie | revokes the family, clears cookies → `204` |
| `GET` | `/auth/me` | access | current `UserOut` |
| `PATCH` | `/auth/me` | access | display name, handle, bio, theme |
| `POST` | `/auth/password` | access | sets/changes password, revokes all sessions → `204` |
| `GET` | `/auth/sessions` | access | active refresh sessions (max 50) |
| `DELETE` | `/auth/sessions/{id}` | access | revokes one session → `204` |
| `GET` | `/health` | none | `{status, checks: {db, cache}, version}`, `503` when degraded |

### UserOut

```json
{
  "id": "0d3f...uuid",
  "phone": "+989121234567",
  "email": null,
  "roles": ["student"],
  "profile": {"display_name": "", "handle": null, "bio": "", "theme": "system",
              "avatar_url": null},
  "date_joined": "2026-11-03T02:00:00+03:30",
  "has_password": true
}
```

### TokenOut

```json
{"access_token": "eyJ...", "token_type": "bearer", "expires_in": 900,
 "user": {"...": "UserOut"}}
```

## Rate limits

Fixed windows in Redis. Exceeding a limit returns `429` with the stable codes below.

| Scope | Limit |
|---|---|
| OTP request per phone (burst) | 3 / 60s |
| OTP request per phone | 5 / 15 min |
| OTP request per IP | 20 / hour |
| OTP resend cooldown | 60s |
| OTP verify per phone | 15 / 10 min |
| OTP verify per IP | 60 / 10 min |
| OTP attempts per code | 5, then the code is burned |
| Password login per phone | 10 / 15 min |
| Password login per IP | 30 / 15 min |
| Submissions per user | 10 / min (planned, phase 3) |
| Custom runs per user | 5 / min (planned) |

Codes: `rate_limited`, `otp_too_soon`, `otp_locked`.

## Admin / RBAC

All require an admin (staff or superuser).

| Method | Path | Body |
|---|---|---|
| `POST` | `/admin/rbac/grants` | `{user_id, capability, target_type, target_id}` |
| `DELETE` | `/admin/rbac/grants/{id}` | none |
| `GET` | `/admin/rbac/grants?user_id=` | none |
| `POST` | `/admin/rbac/users/{user_id}/roles` | `{role}` |

`capability` ∈ `edit | publish | supervise`. `target_type` ∈ `track | contest`
(`contest` returns `503` until that app exists). `role` ∈ `student | creator | admin`.

## Pagination

List endpoints accept `?cursor=<opaque>&limit=<1..100>` (default 20) and return
`{next_cursor, results}`. Cursors encode the last `pk`; models must be ordered by `pk` for
stable pages.

## Planned (documented now, built later)

```text
GET    /tracks                          public catalog tree
GET    /courses/{slug}                  SSR payload; 402 for locked lessons
GET    /lessons/{id}                    body only when authorized
POST   /submissions                     Idempotency-Key; 202 {id, status_url, stream_url}
GET    /submissions/{id}                status + per-test results
POST   /submissions/{id}/rejudge        contest supervisor only
POST   /custom-runs                     ephemeral run, not persisted as a submission
GET    /stream/submissions/{id}         SSE: status, test, finished
GET    /stream/contests/{id}/scoreboard SSE: snapshot then deltas
GET    /stream/notifications            SSE: per-user channel
POST   /orders                          create order with price snapshot
POST   /payments                        payment request, returns gateway URL
GET    /payments/callback               gateway redirect, server-side verify
GET    /certificates/{code}             public verification page payload
```

SSE contract: `event:` is one of `snapshot|status|test|finish|ping`, `data:` is JSON, and
the server sends a `ping` every 20s. Clients reconnect with `Last-Event-ID`; the first
event is always a full snapshot so replay is unnecessary.
