# Retained validation helpers

This directory no longer ships the retired `validate_atoms` CLI or its broad
adapter pipeline.

The remaining `validate_atoms_workers` package is an internal shared boundary
for Workbench and Subject/Topics projections. It provides:

- bounded, no-follow reads and safe YAML frontmatter parsing;
- Header grouping and carrier identity checks;
- pinned, byte-exact source admission for the current Graph Rule closure; and
- fence-aware structural validation of Graph Rule bodies.

`schema_authority.json` is the sole admitted support-source manifest. A missing,
changed, duplicated or unverified source remains a visible admission gap; parsing
does not admit it.

Run the focused checks from the repository root:

```sh
engine="$PWD/LAYER_4_ENGINE_STUDIO_C14"
environment="$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"
UV_PROJECT_ENVIRONMENT="$engine/.venv-dev" PYTHONPATH="$engine" \
  uv run --project "$environment" --locked --no-env-file --no-compile-bytecode --no-default-groups --group dev \
    python -B -m unittest discover \
  -s LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms_workers/validate_atoms_workers__tests
```
