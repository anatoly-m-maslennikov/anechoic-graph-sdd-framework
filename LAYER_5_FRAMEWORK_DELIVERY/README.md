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
the builder. Reusing an existing image skips cache cleanup.

Each Test Suite run writes a JSON report under `.anechoic_tmp/test_reports/`
and prints its path. Reports include the phase, outcome, duration, test
counts, and failed module output. The image phase also records the canary result.
