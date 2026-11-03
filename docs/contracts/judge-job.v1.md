# Judge message contract (v1)

Versioned JSON. Producers and consumers both validate `schema_version`. A breaking change
means a new `judge.job.v2` routing key plus a dual-read window of one deploy.

## Job

Routing key: `judge.contest | judge.practice | judge.custom_run | judge.rejudge`
(exchange `judge`, direct). Priority comes from the queue, not the payload.

```json
{
  "schema_version": 1,
  "job_id": "9c1e...uuid",
  "submission_id": 9123,
  "kind": "submission",
  "exercise": {
    "type": "code",
    "time_limit_ms": 2000,
    "memory_limit_mb": 256,
    "checker": {"type": "token", "source_key": null, "float_tolerance": 1e-6},
    "scoring": "subtask",
    "stop_on_first_failure": false,
    "language_multipliers": {"python": 3.0, "java": 2.0, "cpp": 1.0}
  },
  "language": "python",
  "source": {"storage": "s3", "key": "submissions/2026/11/9c1e.py", "sha256": "ab..."},
  "tests": [
    {
      "id": 41,
      "subtask_id": 7,
      "position": 1,
      "input": {"key": "tests/41.in", "sha256": "cd..."},
      "output": {"key": "tests/41.out", "sha256": "ef..."},
      "is_sample": true
    }
  ],
  "subtasks": [{"id": 7, "points": 30, "depends_on": [], "test_ids": [41, 42]}],
  "limits": {
    "max_output_bytes": 67108864,
    "max_source_bytes": 65536,
    "wall_time_factor": 2.5
  },
  "attempt": 1,
  "enqueued_at": "2026-11-03T02:10:00+03:30"
}
```

Rules:

- `source.storage` is `s3` or `inline` (small custom runs). Inline source is capped at
  `limits.max_source_bytes`.
- Test payloads are never inlined for real submissions; only sample runs may be.
- The worker must verify every `sha256` before running. A mismatch is a `SE`, not a
  re-fetch loop.
- `attempt` increments only for infrastructure retries; a message with `attempt > 3` goes
  to the DLQ.

## Result

The worker writes the terminal state to the database and publishes this envelope on Redis
pub/sub channel `judge.result.{submission_id}` (the API consumes it for SSE). The callback
payload is also POSTed to `/internal/v1/judge/results` when
`settings.JUDGE_CALLBACK_URL` is set, signed with `X-Judge-Signature: sha256=<hmac>` over
the raw body using `JUDGE_SHARED_SECRET`.

```json
{
  "schema_version": 1,
  "job_id": "9c1e...uuid",
  "submission_id": 9123,
  "status": "FINISHED",
  "verdict": "WA",
  "score": 70,
  "time_ms": 1450,
  "memory_kb": 41200,
  "compiler_output": null,
  "tests": [
    {"id": 41, "verdict": "AC", "time_ms": 120, "memory_kb": 21000,
     "stdout_preview": "3 4\n", "stderr_preview": null},
    {"id": 42, "verdict": "WA", "time_ms": 130, "memory_kb": 21500,
     "stdout_preview": "7\n", "stderr_preview": null}
  ],
  "subtask_scores": [{"id": 7, "points": 30, "earned": 0}],
  "judged_at": "2026-11-03T02:10:09+03:30"
}
```

`stdout_preview`/`stderr_preview` are present only for sample tests, truncated to 4 KiB.
`compiler_output` is truncated to 16 KiB and only populated for `CE`.

Verdicts: `AC, WA, TLE, MLE, RE, CE, OLE, SE, PE`.

Status transitions: `QUEUED → RUNNING → FINISHED` or `QUEUED → CANCELED`.
`FINISHED` is terminal; a duplicate result for a finished submission is logged and
dropped.

## SQL variant

`exercise.type` becomes `sql`, and the payload swaps `tests` for:

```json
{
  "sql": {
    "schema_sql": "CREATE TABLE ...",
    "seed_sql": "INSERT INTO ...",
    "reference_query": "SELECT ...",
    "order_sensitive": false,
    "statement_policy": "select_only",
    "result_checks": {"column_names": true, "float_tolerance": 1e-6}
  }
}
```

The result uses `rows_compared` instead of `tests`; verdicts are the same set.
