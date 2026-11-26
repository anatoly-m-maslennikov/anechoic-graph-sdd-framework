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
  status: draft
  version: 19
  updated_at: '2026-11-25T10:24:04.712334+00:00'
relations:
  ANSWERS:
  - AN-S-3038

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

Replace `--help` with `local --project-root <root> --run-id <id>` for Local Release, `prepare-local --project-root <root> --run-id <id> --base <commit> --changed-path <path> --port <port>` to prepare its checkout, or `public --project-root <root> --run-id <id>` for Public Release. Use `build-image --project-root <root> --run-id <id>` to build only the image. `run-image` delegates launch to the Engine shared MCP launcher.

The child Contracts define arguments and results for Runtime Images (AN-S-4732),
Local Release (AN-S-3292), and Public Release (AN-S-3293).

Release code imports no Project code outside the Release subtree.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome. Exit 2 means invalid CLI usage. Exit 130 means interruption. `--help` lists the commands and exits 0.

## Claim

### Formal Claim

```python cli
declare_cli_contract(
    interface='release',
    action='dispatch_framework_release',
    runner='uv',
    path='LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
    subcommands={'local': 'C63', 'prepare-local': 'C63', 'public': 'C64', 'build-image': 'C81', 'run-image': 'C81'},
)
```
