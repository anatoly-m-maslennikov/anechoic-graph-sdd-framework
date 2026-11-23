# Repository delivery policy

This operational document defines how the repository moves changes from `amm/dev` (or the legacy `dev` branch) to `main`. The framework overview and documentation map live in the root [README](../README.md).

## Rules

- [Development branch ruleset](https://github.com/anatoly-m-maslennikov/anechoic-graph-sdd-framework/rules/18896762): only `anatoly-m-maslennikov` may create, update, or delete `dev` or `amm/dev`.
- [`main` ruleset](https://github.com/anatoly-m-maslennikov/anechoic-graph-sdd-framework/rules/18897046): `main` has no bypass actors; every update requires a pull request, `PR policy`, and the merge-commit method.
- [Policy workflow](workflows/dev-to-main-policy.yml): `PR policy` passes only for a same-repository `dev → main` or `amm/dev → main` pull request authored by the repository owner. A passing non-draft PR is merged automatically.
- Repository tests and validators are temporarily disabled; no successful PR check currently represents test, evaluation, lint, type-check, cross-platform, or framework-validation evidence.
- [WSL proof workflow](workflows/wsl-proof.yml) runs Engine Studio static and unit QA on a labeled self-hosted Windows/WSL runner. Dispatch it manually and use a successful run on the tested commit as evidence.
- [Release publisher](workflows/publish-release.yml): a protected `main` push that changes the coordinated version contract is checked against the committed release declaration, then creates only a missing immutable tag or GitHub Release at the exact merge SHA. Existing collisions stop; the workflow never writes repository content after merge.

Merge commits are deliberate: development branches are long-lived, so preserving their commits as parents of `main` prevents the history divergence caused by repeated squash or rebase merges.

## Delivery sequence

1. The owner commits and pushes a bounded change to `amm/dev` (or legacy `dev`).
2. The owner opens a ready pull request from that branch to `main`.
3. `PR policy` validates the author, repository, head, and base.
4. No automated repository validation runs while the temporary suspension is active.
5. GitHub Actions enables merge-commit auto-merge.
6. GitHub updates `main` only after the required checks pass.
7. When the coordinated version contract changed, the release publisher rechecks the committed transaction at the merge SHA, verifies or creates the immutable tag, and verifies or creates its GitHub Release.

Pull requests to `main` from any branch other than `dev` or `amm/dev`, or from any other repository or author, are expected to fail `PR policy` and cannot merge.

The operator runs Public Release separately to prepare pull request and Version History drafts from pinned Git evidence. See the [release commands](../LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/README.md#host-commands).

## Temporary validation suspension

Repository validation was explicitly suspended on 2026-08-10 so the current ANECHOIC development line can be delivered while the self-hosting migration backlog is red. The DSET workflow and its required status check are removed for this interval. `PR policy` remains the sole required check, and `Enable auto-merge` remains the delivery action visible on the pull request.

A green pull request during this suspension proves only that the owner-only development-to-main delivery policy passed. It must not be cited as evaluation evidence for repository correctness, test success, validation success, portability, or release readiness.

To restore automated validation, check out the exact head and run the locked [Engine Studio test suite](../LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/README.md#engine-studio-qa) across Linux, macOS, and native Windows. Add the workflow's stable status check to the `main` ruleset.

Keep each package's tests in its `<package name>__tests/` folder. The
production Docker build excludes those folders.

For interactive Engine QA, run from the repository root and select
`LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml` with Ruff's `--config` or
mypy's `--config-file`. Use `python -B` for ad hoc uv runs, or pass
`-X "pycache_prefix=$PWD/.anechoic_tmp/python/bytecode"` to keep bytecode.
The static phase checks launch commands and reports cache folders outside
the Project temporary directory.

## Local source line length check

The check is off by default. To enable it, set
`enforce_source_line_length = true` under `[tool.anechoic.test_suite]` in
`LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine/pyproject.toml`.

Run from the repository root. The check reports new or edited lines over 79
characters in source files and workflows. It includes staged, unstaged, and
untracked source. The default base is `HEAD`. To include commits on a branch,
pass their base commit with `--base`.

```sh
uv tool install editorconfig-checker==3.11.1
engine="$PWD/LAYER_4_ENGINE_STUDIO_C14"
UV_PROJECT_ENVIRONMENT="$engine/.venv-dev" PYTHONPATH="$engine" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-env-file \
    python -B -P -m FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.source_line_length \
    --project-root "$PWD"
```

The check rejects `editorconfig-checker-disable-next-line` directives.
