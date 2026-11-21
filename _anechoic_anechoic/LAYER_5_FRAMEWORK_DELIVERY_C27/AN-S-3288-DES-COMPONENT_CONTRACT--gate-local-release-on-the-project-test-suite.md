---
atom_family: SPEC
atom_id: AN-S-3288
container:
  component: C27
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "active"
  version: 5
  updated_at: '2026-11-21T22:24:03.911363+00:00'
---

## Summary

Gate Local Release on the Project Test Suite

## Guarantee

The Release CLI has one host entry point. Run this command from the Framework checkout with its existing Project launcher environment.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/.anechoic_runtime/launcher-venv" \
  uv run --project "$PWD" --locked --no-sync --python 3.14 \
    --managed-python --no-env-file --all-groups \
    python -B "$PWD/LAYER_5_FRAMEWORK_DELIVERY/release.py" --help
```

Replace `--help` with `local --project-root <root> --run-id <id>` for Local Release or `public --project-root <root> --run-id <id>` for Public Release. Use `build-image --project-root <root> --run-id <id>` to build only the image.

The child CLI Contracts define the additional arguments and result guarantees.

The host dispatches to C63 or C64. Release code imports no Project code outside the Release subtree. C63 calls C19 Test Suite through its command interface; C64 calls no subsystem.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome. Exit 2 means invalid CLI usage. Exit 130 means interruption. `--help` lists the commands and exits 0.

## References

AN-S-3292@3, AN-S-3293, AN-S-1976, and AN-S-1994.
