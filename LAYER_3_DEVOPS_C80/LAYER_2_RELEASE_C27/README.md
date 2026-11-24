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

Local Release runs the `static` phase and then the `functional` phase with
the configured host checks. After both pass, it builds the candidate and
runs the `image` phase against its exact image ID. Installation requires
passing image tests and the canary.

Use `prepare-local --run-id <id> --base <full-commit> --changed-path <path>`
with `--port <loopback-port>` to prepare an isolated Local Release checkout.
Repeat `--changed-path` for each literal repository-relative file.
An absent source file removes that file from the base.

Preparation commits the specified paths and the isolated Manifest port
in a private temporary checkout outside the source Project. The JSON
result gives its `project_root` and exact `revision`. Run the existing
`local` command from that checkout with its own Release script.
Preparation ends after commit verification. Local Release handles the
port binding, image build, and installation.

Before a fresh image build, Local Release and the Engine build command
ask Docker to trim unused build cache to 4 GB and free at least 2 GB on
the builder. Local Release applies the same limits after the new runtime
is healthy on the production port and its image is tagged as production.

Final Local Release cleanup deletes scratch files under `.anechoic_tmp/`
with a modification time more than 48 hours old. It keeps the release and
lifecycle locks, the shared uv cache, the Playwright browser install, and
resumable Atom Review state. The cleanup does not follow symbolic links.

Each Test Suite run writes a JSON report under `.anechoic_tmp/test_reports/`
and prints its path. Reports include the phase, outcome, duration, test
counts, and failed module output. The image phase also records the canary result.

The image tests launch the pinned Chromium through Playwright before running
the Workbench browser cases. Run the image phase in a host context that permits
Chromium subprocesses. In a managed shell, the launcher may need host approval.
