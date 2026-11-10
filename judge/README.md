# Judge worker

Placeholder for weeks 5–8. The worker will be a Celery app consuming
`judge.contest`, `judge.practice`, and `judge.custom_run`, talking to go-judge over HTTP and
to the isolated SQL-judge PostgreSQL. The message format is fixed in
`docs/contracts/judge-job.v1.md`; the compose wiring is in `infra/docker-compose.judge.yml`.
