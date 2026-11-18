# Branch protection checklist

Apply manually in GitHub: Settings > Branches > Add rule (or Rulesets) for `main`.

## Required settings

- [ ] Require a pull request before merging (at least 1 approval).
- [ ] Require status checks to pass before merging:
  - `ci / backend`
  - `ci / frontend`
- [ ] Require branches to be up to date before merging.
- [ ] Do not allow force pushes.
- [ ] Do not allow deletions of `main`.

## Repository settings (Settings > General > Pull Requests)

- [ ] Allow squash merging only (disable merge commits and rebase merging).
- [ ] Default squash commit message: "Pull request title".
- [ ] Automatically delete head branches.

## Notes

- Check names come from the workflow name (`ci`) and job ids (`backend`, `frontend`)
  in `.github/workflows/ci.yml`. A check only appears in the picker after it has run once.
- Do not require `ci / images`. It runs only on `push` to `main` and is skipped on pull
  requests, so requiring it would block every PR.
- `deploy` is triggered by `workflow_run` of `ci` on `main`; it is not a PR check.
- Security-relevant PRs (judge, payments, auth) need a second reviewer by convention;
  GitHub can enforce this with CODEOWNERS if desired.
