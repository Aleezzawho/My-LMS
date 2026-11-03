# LMS Platform — Engineering Documentation

Persian-first (RTL) interactive LMS + automated judge. Django modular monolith with a
separate judge worker fleet. See the master prompt for product scope.

| Document | Contents |
|---|---|
| `design.md` | Architecture, module boundaries, sequence diagrams |
| `erd.md` | Data model (Mermaid ERD) and modelling rules |
| `repository.md` | Monorepo layout, conventions, branching, CI gates |
| `api.md` | REST surface, auth, pagination, rate limits, SSE |
| `contracts/judge-job.v1.md` | Judge job/result message contract |

Status: phase 1 (weeks 1–2) implemented. Auth, OTP, RBAC, i18n/RTL shell, CI, and local
compose stack are in place; catalog/judge/contests land in later phases.
