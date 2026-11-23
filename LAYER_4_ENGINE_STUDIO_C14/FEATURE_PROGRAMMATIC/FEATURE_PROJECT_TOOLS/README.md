# Project release tools

These tools belong to the `anechoic` Project, not the reusable Framework
package. Shared compiler, installer and test-gate helpers remain in the Engine.

## Two workflows

- **Local release:** first commit all tracked changes and untracked nonignored
  files, then verify a clean worktree and index. A clean repository needs no
  empty commit; a failed commit or remaining changes stop before tests, builds
  or Docker work. Run the functional phase before preparing the package and
  image. Copy active Methodology sources, compile the product, and build the
  Engine package and candidate image. Run end-to-end checks and test the candidate
  against a disposable Project copy on a Docker-assigned loopback port. After
  it passes, install the Methodology and Project runtime and verify MCP. Preserve configuration and
  remove eligible stopped obsolete Project-owned containers before MCP startup,
  then repeat cleanup after the new production image passes its smoke test. Keep
  the current image and two previous Project images. Use verified release history
  first and fill any remaining slots from the newest Project-owned images. Preserve every container
  reference, other Projects' images, other running containers and unproven
  targets; report unfinished cleanup. Never force removal or prune globally.
- **Public release:** read completed Task and Epic evidence at pinned Git commits.
  Use the evidence and pinned diff to review changes. Submit the reviewed changes
  to get Markdown drafts for a pull request description and Version History entry.
  The Operator handles publication.

Local checkpoints keep existing ignored-file and environment-file exclusions.
Excluded nonignored changes stop release rather than being committed or waived.

The full suite discovers and runs the retained test modules. Each module has a
finite 60-minute budget. Host and Docker pools are bounded separately, and the
same immutable test image is shared by disposable Project stacks.

Fresh Local-release image builds carry exact Project ownership, Project name and
the full build-time owning-repository HEAD commit ID; missing or invalid name or
HEAD stops fresh preparation before building. Name and HEAD record provenance;
the source fingerprint and immutable image ID identify built bytes. Canonical
images use `version-test-builddate-digest` until the release verifies the
running MCP and changes the exact candidate tag to `version-prod-builddate-digest`.
The UTC build date uses `YYYY-MM-DD_HH-MM-SSZ`. Release retention applies to
the exact admitted candidate.
Complete matching Project/root/control ownership labels allow
cleanup to identify labelled orphan images. Cached images keep their existing
labels and reuse behavior; no metadata-only rebuild or ownership claim is added.
Legacy unlabelled or otherwise unproven images remain retained and reported,
even if a Project container formerly referenced them. Image cleanup is skipped
unless the replacement launcher has verified the exact candidate image.

The Release Project owns `LAYER_2_LOCAL_RELEASE_C63/local_release.py` and
`LAYER_3_PUBLIC_RELEASE_C64/public_release.py`. Run them through `release.py` on the host
with an Operator-selected `--run-id`. Local Release writes its own receipts.

The host commands below are the release entry point for this Project. Release
operations are not exposed through the retained Workbench MCP surface.

## Host commands

Run these commands from the repository root in the locked `release` environment.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -B LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py local --run-id local-001
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -B LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py public --run-id public-001
```

Local Release defaults to `--image-mode refresh` and uses the checked-in
registry. Use the Engine Studio test suite directly for focused runs. The
Local Release compatibility option `--test-module` leaves its gate unchanged.

For a release that predates these Git snapshots, recover its generated files
from the known-good image with `docker create` and `docker cp`. The files are
under `/workspace` at their checkout-relative paths. The temporary container
can stay stopped.

Use `build-image` to get the immutable image ID without deploying it or changing
the Version.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -B LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py build-image --run-id image-001
```

`--project-root PATH` is optional; the default is this repository's root, derived
from the script location. Choose a new run ID for each new release; simple IDs
such as `local-001` and `public-001` work for both commands.

Public Release defaults to `--base origin/main` and `--head amm/dev`. The first
run returns `input_required` with the commit pins, the evidence, and the schema
for the reviewed changes. Rerun with `--content-draft /absolute/path/draft.json`.
The file must be regular UTF-8 JSON, at most 1 MiB, and contain `base_commit`,
`head_commit`, and `changes`. Use the same commit pins and mark one to five of
the changes as highlights for the Version History.

The commands return JSON on stdout. Exit status is zero for `completed`.

Local release reports phase and test-module progress on stderr. Its full test
output is streamed to a log under `.anechoic_tmp/simple_local_release`, with
the location printed before testing starts. Interruption during release execution
retains that log and a failure report and exits 130. It stops the owned test
processes. Earlier release changes remain available for manual handling.

Release effects run on the host with Git and Docker. Local Release checkpoints
safe, nonignored changes. Public Release reads Git and returns the drafts in JSON.

## Kept small

These repository commands are separate from MCP.
Automatic recovery/resume and legacy-layout compatibility are deferred.
Failures stop and report the actual failed step for manual handling.

## Engine Studio QA

Run the required unit selection from the repository root in the locked `dev` environment.
Use `--phase static` for static checks and static test modules.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-env-file \
    python -B -P -m FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__pub \
    --project-root "$PWD" --phase unit --required
```

For a focused Engine Studio run, use `--phase unit --test-module PATH`. Use
repository-relative test paths and repeat `--test-module` to select more modules.
The default unit phase runs discovered host tests. Component test packages may
place tests in `static/`, `unit/`, and `image/`; flat host tests remain unit tests.
When `lean` is on PATH, static checks reject confirmed state-boundary violations
and witnessed silent actions. An `anechoic: no-op` comment directly above an action
declares intentional silence. Workbench and MCP expose the ordered evidence in
`state_effect_findings`. Unsupported paths and unavailable tools remain unresolved.
The image phase requires `--candidate-image` with an immutable sha256 image ID,
`--canary-package`, `--canary-selection` as JSON, and `--run-id`. It runs image
tests and then the canary; required skips fail.

## Source comments

Engine QA Standard AN-S-3183 defines the source comment rule.
The full suite reports ordinary comments in the Engine and Delivery source.
The check covers Python, Docker recipes, and the JavaScript, TypeScript, Svelte,
CSS, and HTML sources. It retains executable and tooling directives and reports
any CSS comment that needs a manual edit to preserve token boundaries.

Run the same check from the Project root with the locked Python environment and
the Workbench frontend dependencies installed. Add `--fix` to remove reported
comments.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-env-file \
    python -B -P -m FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.source_comments \
    --project-root "$PWD"
```

## macOS temporary files

Use `.anechoic_tmp` for Project scratch. If an external tool leaves a completed
run in a private directory directly under `/private/tmp`, mark that directory
for the daily BB cleanup. Set `completed_run_dir` to its absolute path and run
this from the Project checkout.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-env-file \
    python -B -P -m FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.prune_private_tmp \
    --mark "$completed_run_dir"
```

Cleanup removes marked directories after three days. Registered worktrees,
Docker mounts and open files protect their directories from cleanup.
