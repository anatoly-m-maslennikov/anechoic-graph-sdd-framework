---
atom_family: SPEC
atom_id: AN-S-3038
container:
  component: C80
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 12
  updated_at: '2026-11-28T10:15:18+00:00'
---

## Summary

Declare Release

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C27',
    name='Release',
    layer=2,
    lens_whitelist=['DevOps'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['C27', 'C81', 'C63', 'C64']},
          'exports': {'LAYER_2_RELEASE_C27__shared': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_RELEASE_C27__tests']}}},
 'io': {'server': {'release': {'transport': 'cli',
                               'runner': 'uv',
                               'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                               'subcommands': {'local': 'C63',
                                               'prepare-local': 'C63',
                                               'verify-image': 'C63',
                                               'public': 'C64',
                                               'build-image': 'C81',
                                               'run-image': 'C81'}}}}}
```

## Component Contract

### Dispatch Release and Runtime Image commands

#### Guarantee

Run `./release__public --help` from the Framework checkout root. The
launcher opens the Release CLI in the locked `release` environment.

Use `local --project-root <root> --run-id <id>` for a same-Project release.
For an explicit target, use
`local --project-root <source> --source-revision <full SHA> --target-project-root <target> --run-id <id>`.
Continue with `--resume`, the same Run ID, and the same Project bindings.
For a split run, pass the current exact source revision. After delivery starts,
pass the revision recorded at the delivery claim.

Use `verify-image --project-root <source> --run-id <id>` for the image
gate. Use `prepare-local --project-root <source> --run-id <id>` with an
exact base, changed paths, and an isolated port. C63 handles these commands.

Use `public --project-root <root> --run-id <id>` for Public Release
through C64. Use `build-image --project-root <root>
--run-id <id>` to build an image through C81 under AN-S-4732.
`run-image` delegates launch to the Engine shared MCP launcher.

Release code imports no Project code outside the Release subtree.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome. Exit 2 means invalid CLI usage. Exit 130 means interruption. `--help` lists the commands and exits 0.

The formal cases cover standard dispatch and reporting. The Local Release
Contract governs the path for each continuation and maintenance operation.
The interruption case reports a failed JSON result and exit 130.

```python cli
declare_cli_contract(
    interface='release',
    action='dispatch_framework_release',
    exit_codes={'completed': 0, 'incomplete': 1, 'interrupted': 130},
    stdout='json_object',
)
```
