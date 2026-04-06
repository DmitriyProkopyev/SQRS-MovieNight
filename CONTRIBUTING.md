The following is a concise guide for project contributors.


### Local pre‑commit setup

To ensure consistent code quality and security checks, contributors must install a local `pre-commit` hook using the command below.

Run this once in the root of the repository:

```bash
chmod +x ./contributor_setup.sh
bash ./contributor_setup.sh
```

This command sets up the pre-commit hook that will **block commits if linting or security checks fail**.

> Note: Linting and security scanning are also performed in the CI pipeline on `main` pull requests for consistency. Prefer, however, to catch related issues locally.

### Branching rules and workflow

- **Direct commits into `main` are not allowed.**
  All changes to `main` must go through a pull request.

- **Pull requests into `main` should be created from the `dev` branch.**
  In other words, your workflow should look like:
  1. Create a feature branch from `dev` or work directly in `dev`.
  2. Commit and push your changes.
  3. Create a pull request from `dev` into `main`.
  4. Ensure that the CI pipeline passes on yuor changes.
  5. Obtain approving PR review from at least two team members.

- Direct commits into `dev` and its child branches are allowed.

Avoid force pushes or bypassing CI quality gates.
