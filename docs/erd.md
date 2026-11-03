# Data Model

```mermaid
erDiagram
  USER ||--|| PROFILE : has
  USER ||--o{ OTP_REQUEST : requests
  USER ||--o{ REFRESH_SESSION : holds
  USER ||--o{ OBJECT_PERMISSION : granted
  USER }o--o{ GROUP : member

  TRACK ||--o{ COURSE : contains
  COURSE ||--o{ CHAPTER : contains
  CHAPTER ||--o{ LESSON : contains
  LESSON ||--o{ LESSON_EXERCISE : links
  EXERCISE ||--o{ LESSON_EXERCISE : appears_in
  COURSE ||--o{ ENROLLMENT : sold_as
  USER ||--o{ ENROLLMENT : buys
  USER ||--o{ LESSON_PROGRESS : reads
  USER ||--o{ EXERCISE_PROGRESS : solves

  EXERCISE ||--o| QUIZ
  QUIZ ||--o{ QUIZ_QUESTION
  QUIZ_QUESTION ||--o{ QUIZ_CHOICE
  EXERCISE ||--o| CODE_PROBLEM
  CODE_PROBLEM ||--o{ TEST_CASE
  CODE_PROBLEM ||--o{ SUBTASK
  EXERCISE ||--o| SQL_PROBLEM
  EXERCISE ||--o{ HINT
  USER ||--o{ HINT_UNLOCK : unlocks

  USER ||--o{ SUBMISSION : submits
  EXERCISE ||--o{ SUBMISSION : receives
  SUBMISSION ||--o{ TEST_RUN_RESULT : produces
  CONTEST ||--o{ CONTEST_PROBLEM : includes
  EXERCISE ||--o{ CONTEST_PROBLEM : used_in
  CONTEST ||--o{ CONTEST_PARTICIPATION : has
  USER ||--o{ CONTEST_PARTICIPATION : joins
  CONTEST ||--o{ CLARIFICATION : has
  CONTEST ||--o{ RATING_RECORD : rates
  USER ||--o{ RATING_RECORD : holds

  USER ||--o{ XP_EVENT : earns
  USER ||--o| STREAK : maintains
  USER ||--o{ USER_BADGE : earns
  BADGE ||--o{ USER_BADGE : awarded

  USER ||--o{ COMMENT : writes
  USER ||--o{ FORUM_TOPIC : starts
  FORUM_TOPIC ||--o{ FORUM_POST : contains
  USER ||--o{ FORUM_POST : writes
  USER ||--o{ VOTE : casts

  USER ||--o{ ORDER : places
  ORDER ||--o{ ORDER_ITEM : contains
  ORDER ||--o{ PAYMENT : paid_by
  DISCOUNT_CODE ||--o{ DISCOUNT_REDEMPTION : redeemed
  USER ||--o{ CERTIFICATE : earns
```

## Modelling rules

1. **Double key.** Internal `BigAutoField` PK for joins and FKs; `public_id` UUID exposed in
   URLs and API payloads. Sequential IDs in URLs leak volume and invite enumeration; UUID
   joins are slower and larger, so we keep both.
2. **Money in rials, integer.** `price_irr` is a `PositiveIntegerField`; no floats anywhere
   in commerce.
3. **Price snapshot.** `OrderItem.unit_price_irr` copies the price at purchase time, so a
   later price change never rewrites history; `Order.total_irr` is the sum at creation.
4. **Test data by reference.** `TestCase.input_key`/`output_key` are S3 keys plus a
   `sha256` of the content for the judge's local cache and integrity checks. Inputs are
   never stored in Postgres.
5. **Timestamps.** `created_at`/`updated_at` on everything mutable; `created_at` indexed on
   high-volume tables (submissions, xp events, comments).
6. **Soft delete** only for user-generated text (`Comment.is_deleted` keeps the thread
   shape). Content rows are hard-deleted but protected if they have submissions.
7. **Idempotency.** `Submission.idempotency_key` unique per user; `Payment.authority`
   unique; `XpEvent` unique on `(user, source_type, source_id)`.
8. **Partial scores.** `ExerciseProgress.best_score` and `Submission.score` are integers
   0–100, so IOI subtasks and quizzes share one progress model.

## Core tables

### accounts (implemented)

| Column | Type | Notes |
|---|---|---|
| `id` | bigint PK | internal |
| `public_id` | uuid unique | API identifier |
| `phone` | varchar(16) unique | E.164, normalized to `+989...` |
| `email` | varchar(254) unique null | lowercased by the manager |
| `password` | varchar(128) | Argon2; unusable for OTP-only users |
| `is_active`, `is_staff`, `is_superuser` | bool | |
| `date_joined` | timestamptz | |

`profile(user_id, display_name, handle unique, bio, avatar_key, theme)`

`otp_request(phone, purpose, code_hash, attempts, max_attempts, expires_at, requested_ip,
consumed_at, delivery_ref)`, indexed on `(phone, purpose, created_at)`

`refresh_session(user_id, jti, family, parent_id, expires_at, revoked_at, revoked_reason,
last_used_at, user_agent, ip)`, indexed on `(user_id, family)`. Rotation inserts a child
row; reuse revokes the whole family.

### rbac (implemented)

`object_permission(user_id, capability, content_type_id, object_id, granted_by_id)` with a
unique constraint on `(user, capability, content_type, object_id)`. The generic FK keeps
`rbac` from importing `catalog` or `contests`.

## Planned tables (phase 3+)

```text
track(id, public_id, slug, title, description_mdx, cover_key, owner_id, is_published)
course(id, public_id, track_id, slug, title, summary, price_irr, free_chapter_count,
       owner_id, revenue_share_bps NULL, is_published)
chapter(id, course_id, position, title, is_free)
lesson(id, chapter_id, position, slug, title, mdx_source, rendered_html, video_id,
       estimated_minutes, is_free, published_at)
exercise(id, public_id, type, title, statement_mdx, difficulty, xp_reward, visibility)
test_case(id, code_problem_id, subtask_id NULL, position, input_key, output_key,
          input_sha256, is_sample)
submission(id, public_id, user_id, exercise_id, contest_id NULL, language, source,
           status, verdict, score, time_ms, memory_kb, idempotency_key, judged_at)
```

Each table keeps the internal key plus `public_id`; `submission.idempotency_key` is unique
per `(user_id, idempotency_key)`.
