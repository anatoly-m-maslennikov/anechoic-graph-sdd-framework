# Operator Documentation

## Resume Local Release

Start a Local Release with a run ID. If a phase fails, the release stops and
reports the phase, its error, and the run ID. Fix the cause, then run the
same [host Release command](../LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/README.md)
with `local --resume --run-id <id>` from the same checkout.

Repeat this cycle after each failure with the same run ID. The journal keeps
the target Project, allocated version, phase evidence, package, and exact
image. Resume reuses completed phases whose inputs and evidence still match.
When only the canary inputs change, continue with the same image and its
passing image tests. Runtime changes require a new image and image checks.

Once installation starts, resume with the recorded artifact. Local Release
checks the files and container before repeating an effect. After verified
startup, a cleanup failure resumes cleanup alone. Use a new run ID for a
different target or a separate release.

If the initial command failed to select a Project, correct the Project
Manifest and repeat the initial command. Resume needs an existing journal.

## Verify an image

Use `verify-image --project-root <source> --run-id <id>` with the same
host Release command. It builds the candidate and runs the official image
suite and canary. The source version and installed runtime stay unchanged.

Local Release and image verification check pinned Chromium, DuckPGQ, and
locked frontend dependencies at the start. Use the reported setup or cache
path to fix a prerequisite before rerunning the command.

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
