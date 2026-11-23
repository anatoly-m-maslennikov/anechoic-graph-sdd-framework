# Release environment

Run Release from any directory with its own locked environment:

```sh
root=/absolute/path/to/checkout
UV_PROJECT_ENVIRONMENT="$root/LAYER_5_FRAMEWORK_DELIVERY/.venv-release" \
  uv run --no-compile-bytecode --project "$root/LAYER_3_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -X "pycache_prefix=$root/.anechoic_tmp/cache/python" \
    "$root/LAYER_5_FRAMEWORK_DELIVERY/release.py" --help
```

`UV_PROJECT_ENVIRONMENT` preserves the Release environment in the delivery layer. Local Release runs Engine test gates in Engine Studio's `.venv-dev`. Release commands can change the selected Project; consult their arguments before running them.

`project.toml` selects the Current or Beta stack when building an image.
The image records the selected stack for runtime dispatch.

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
