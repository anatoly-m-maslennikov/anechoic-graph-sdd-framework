# Operator Documentation

## Local Release

From the target checkout, run `./release__public local`. It prints the run ID.
You can supply `--run-id <id>` to choose one. If a phase fails, fix the cause and
run `./release__public local --continue`. Use `./release__public local --status` to inspect
its phase and logs.

To request a stop before delivery, run `./release__public local --abort`. A running
test group stops promptly. Other operations stop at their next checkpoint.
Logs and the installed runtime are preserved. Continue can resume the run.
Abort is refused after the delivery claim.

Controls select the one open, nonsuperseded target run. If more than one is
eligible, pass `--run-id <id>`. Continue reuses passing phase evidence whose
inputs still match. Once delivery starts, it uses the accepted artifact.
If start fails before it records a run, fix the reported input and start again.

Use `./release__public local --suite fast` for recent-failure Test Packages and
a reproducible 10% sample. Static checks, packaged boundary tests, and the
MCP canary still run. Continue keeps the recorded suite and selection.
The receipt measures time from start to production readiness. Ten minutes is
ideal and fifteen minutes is mandatory. An overrun is a QA performance miss.
Verification and delivery continue under their normal gates.

To release selected changes, use `./release__public local --base <full-sha>
--changed-path <file>`, repeating `--changed-path` for each literal path.
The base must include the ancestry required by the tests. The private candidate
alone gets the version bump and keeps the target Manifest port. Commit fixes
in the exact source checkout reported by the run, then continue from the
target. Delivery freezes the accepted source SHA.

Missing pinned Engine, frontend, Chromium, and DuckPGQ prerequisites are
prepared before the first preflight. Release reuses configured prerequisites.
Use a host context that permits Chromium to launch. Lean must be on `PATH`
or set by `LEAN_BIN` for its gate. The [Release guide](../LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/README.md)
also describes the supported lower-level commands and explicit preparation.

## Verify an image

Use `verify-image --project-root <source> --run-id <id>` with the same
host Release command. It builds the candidate and runs the official image
suite and canary. The source version and installed runtime stay unchanged.

Local Release and image verification check pinned Chromium, DuckPGQ, and
locked frontend dependencies at the start. Run `local --prepare-environment
--project-root <source> --run-id <id>` to set up and recheck these prerequisites.

## Release to a selected Project

From the clean source checkout, use `local --project-root <source>
--source-revision <full-sha> --target-project-root <target> --run-id <id>`.
Use the same source and target roots on resume. Before installation, supply
the full SHA of the corrected, clean source checkout. Keep the same version.
Once installation starts, keep the accepted source revision, target runtime
settings, and test environment.

Release preserves the target Manifest, port, authoring files, and data.
The receipt records the accepted source revision, the revision that built
the exact image, the target Project, and container readiness. Failure reports
keep bounded startup diagnostics.
