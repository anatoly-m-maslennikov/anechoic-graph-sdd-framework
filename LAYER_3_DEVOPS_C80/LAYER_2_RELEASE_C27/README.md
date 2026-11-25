# Release environment

Run Release from any directory with its own locked environment:

```sh
root=/absolute/path/to/checkout
UV_PROJECT_ENVIRONMENT="$root/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release" \
  uv run --no-compile-bytecode --project "$root/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -X "pycache_prefix=$root/.anechoic_tmp/python/bytecode" \
    "$root/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py" --help
```

`UV_PROJECT_ENVIRONMENT` preserves the Release environment in the delivery layer. Local Release runs Engine test gates in Engine Studio's `.venv-dev`. Release commands can change the selected Project; consult their arguments before running them.

`project.toml` selects the Current or Beta stack when building an image.
The image records the selected stack for runtime dispatch.

Runtime Images provides the `build-image` and `run-image` commands. User
Setup uses both commands, and Local Release uses the same image layer for
its candidate and production container.

`local`, `build-image`, `verify-image`, and `run-image` accept
`--engine orbstack` or `--engine docker`. On macOS, OrbStack is the
default and `docker` selects Docker Desktop. On other platforms, Docker
is the default. The flag selects the context for this command.

Local Release runs Static, then required Functional tests. After both pass,
it builds the candidate, runs the image tests against its exact image ID,
and runs the MCP canary. Image tests and the canary have separate
checkpoints and logs. Installation requires both to pass.
When an older source offers only the combined image phase, its passing
result supplies both checkpoints.
Local Release gives the installed runtime up to 15 minutes to become ready.

After a failure, fix the cause and run `local --resume --run-id <id>`
with the original run ID, Project root, and engine. Repeat after each failure.
Continue uses the recorded version and any passing phase evidence whose
inputs still match. See
[Operator Documentation](../../LAYER_6_OPERATOR_DOCUMENTATION_C25/README.md).

Use `local --status --run-id <id>` to read the recorded phase, test logs,
candidate image, and outcome. For a split release, pass the destination
as `--project-root`. The working phase is the last phase started in the
journal. It can remain set after interruption. `release_outcome` records
the release result. The command's exit code reflects the status read.

Use `verify-image --run-id <id>` for a candidate build, image tests, and
canary without installation. Local Release and image verification check
the pinned browser, DuckPGQ, and frontend dependencies before the gates.

Use `local --source-revision <full-sha> --target-project-root <target>
--run-id <id>` from the clean source checkout to release its exact revision
to another Project. On resume, keep both Project roots and the allocated
version. Before delivery, pass the full SHA of the clean checkout with
the fix. After delivery starts, keep the accepted SHA.

Use `prepare-local --run-id <id> --base <full-commit> --changed-path <path>`
with `--port <loopback-port>` to prepare an isolated Local Release checkout.
Repeat `--changed-path` for each literal repository-relative file.
An absent source file removes that file from the base.

Preparation commits the specified paths and the isolated Manifest port
in a private temporary checkout outside the source Project. The JSON
result gives its `project_root` and exact `revision`. Run the existing
`local` command from that checkout with its own Release script.
For OrbStack watcher checks, set `TMPDIR` to a private directory under
your home directory before running `prepare-local`.
Preparation ends after commit verification. Local Release handles the
port binding, image build, and installation.

Run `local --prepare-environment --project-root <checkout> --run-id <id>`
to provision the locked Engine and frontend dependencies, pinned Chromium,
and DuckPGQ. It finishes by running the checkout's existing preflight.
Run it in a host context that permits Chromium to launch.

Before a fresh image build, Local Release and the Engine build command
ask Docker to trim unused build cache to 4 GB and free at least 2 GB on
the builder. Local Release applies the same limits after the new runtime
is healthy on the production port and its image is tagged as production.

Each image build removes regular `.DS_Store` files and empty directories
from its private build context before invoking the builder. Release also
removes Finder metadata when it clears its temporary staging directory.

Final Local Release cleanup deletes scratch files under `.anechoic_tmp/`
with a modification time more than 48 hours old. It keeps the release and
lifecycle locks, the shared uv cache, the Playwright browser install, and
resumable Atom Review state. The cleanup does not follow symbolic links.

Each Test Suite run writes a JSON report under `.anechoic_tmp/test_reports/`
and prints its path. Reports include the phase, outcome, duration, test
counts, and failed module output. The canary report records its MCP result.

The image tests launch the pinned Chromium through Playwright before running
the Workbench browser cases. Run the image phase in a host context that permits
Chromium subprocesses. In a managed shell, the launcher may need host approval.
