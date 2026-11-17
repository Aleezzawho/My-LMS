You are working on the project described in docs/MASTER_PROMPT.md. Read that file completely before doing anything else, and treat every decision in it as final (Working Rules §0 apply).

TASK 0 — Orientation (NO implementation code yet):

1. Inspect the current repository state and report:
   - What exists right now (folders, files, git branches, last commits).
   - Whether Docker, Node, Python 3.12 and Git are available on this machine (run the version commands).
   - Anything in the repo that conflicts with the master prompt.

2. Produce ONLY these two deliverables from §14, as files in docs/:
   - docs/technical-design.md — architecture, module boundaries, and Mermaid sequence diagrams for: submission judging, contest scoring, payment (Zarinpal), OTP login.
   - docs/repo-structure.md — the monorepo layout (backend/, frontend/, judge/, infra/, docs/) with conventions: lint, format, commit style, branching.

3. List every ambiguity or risk you found in the master prompt as "Assumptions" and "Open Questions" at the end of your report. Do not silently change any decision; if you disagree with one, explain why and propose an alternative.

Constraints: work on a new git branch `docs/task-0-design`, commit in small commits, and do not start ERD, API spec, infra files, or any phase work. When finished, give me a short summary and the exact next step you recommend.