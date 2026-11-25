---
atom_family: SPEC
atom_id: AN-S-3288
container:
  component: C27
tier: 0
context:
  template: component_contract
  lens: DevOps
state:
  status: archived
  version: 14
  updated_at: '2026-11-23T14:45:10.920666+00:00'
relations:
  ANSWERS:
  - AN-S-3038
  IS_REFERENCE:
  - AN-S-4732
  - AN-S-3292@9
  - AN-S-3293
---

## Summary

Dispatch Release and Runtime Image commands

## Guarantee

The Release CLI has one host entry point. Run this command from the Framework checkout root in the `release` environment.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release" \
  uv run --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -B "$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py" --help
```

Replace `--help` with `local --project-root <root> --run-id <id>` for Local Release or `public --project-root <root> --run-id <id>` for Public Release. Use `build-image --project-root <root> --run-id <id>` to build only the image. `run-image` delegates launch to the Engine shared MCP launcher.

The child Contracts define arguments and results for Runtime Images (AN-S-4732),
Local Release (AN-S-3292), and Public Release (AN-S-3293).

The host dispatches image commands to C81, Local Release to C63, and Public Release to C64. Release code imports no Project code outside the Release subtree.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome. Exit 2 means invalid CLI usage. Exit 130 means interruption. `--help` lists the commands and exits 0.
