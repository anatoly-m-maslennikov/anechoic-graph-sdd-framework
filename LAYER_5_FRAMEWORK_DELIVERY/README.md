# Release environment

Run Release from any directory with its own locked environment:

```sh
UV_PROJECT_ENVIRONMENT=.venv-release uv run --project /absolute/path/to/LAYER_5_FRAMEWORK_DELIVERY --locked python /absolute/path/to/LAYER_5_FRAMEWORK_DELIVERY/release.py --help
```

`UV_PROJECT_ENVIRONMENT` is relative to the Release project. Local Release runs Engine test gates in Engine Studio's `.venv-dev`. Release commands can change the selected Project; consult their arguments before running them.
