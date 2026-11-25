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
  status: active
  version: 18
  updated_at: '2026-11-24T18:19:55.278865+00:00'
relations:
  ANSWERS:
  - AN-S-3038
  IS_REFERENCE:
  - AN-S-4732
  - AN-S-3292@13
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

Use `local --project-root <root> --run-id <id>` for a same-Project release.
For an explicit target, use
`local --project-root <source> --source-revision <full SHA> --target-project-root <target> --run-id <id>`.
Continue with `--resume`, the same Run ID, and the same Project bindings.
For a split run, pass the current exact source revision. After delivery starts,
pass the revision recorded at the delivery claim.

Use `verify-image --project-root <source> --run-id <id>` for the image
gate. C63 handles these commands under AN-S-3292.

Use `public --project-root <root> --run-id <id>` for Public Release
through C64 under AN-S-3293. Use `build-image --project-root <root>
--run-id <id>` to build an image through C81 under AN-S-4732.
`run-image` delegates launch to the Engine shared MCP launcher.

Release code imports no Project code outside the Release subtree.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome. Exit 2 means invalid CLI usage. Exit 130 means interruption. `--help` lists the commands and exits 0.
