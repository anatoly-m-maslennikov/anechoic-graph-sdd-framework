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
  version: 10
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare Release

## Purpose

Dispatch Framework Release and Runtime Image commands through one host entry point.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C27',
        name='Release',
        layer=2,
        lens_whitelist=['DevOps'],
    ),
)
```

## Component Boundaries

Release code imports no Project code outside the Release subtree.

The checkout's `release__public` launcher uses the locked `release` environment.

    ./release__public --help

```python
{
    'code': {
        'exports': {
            'LAYER_2_RELEASE_C27__shared': {
                'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_RELEASE_C27__tests'],
            },
        },
        'imports': {'only': ['C27', 'C81', 'C63', 'C64']},
    },
    'io': {
        'server': {
            'release': {
                'transport': 'cli',
                'runner': 'uv',
                'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                'subcommands': {
                    'local': 'C63',
                    'prepare-local': 'C63',
                    'public': 'C64',
                    'build-image': 'C81',
                    'verify-image': 'C63',
                    'run-image': 'C81',
                },
            },
        },
    },
}
```

## Component Contract

- `local --project-root <root> --run-id <id>` runs Local Release.
- `prepare-local --project-root <root> --run-id <id> --base <commit> --changed-path <path> --port <port>` prepares its checkout.
- `public --project-root <root> --run-id <id>` runs Public Release.
- `build-image --project-root <root> --run-id <id>` builds an image.
- `verify-image --project-root <root> --run-id <id>` runs the isolated image gate.
- `run-image --image <image>` selects an image to launch. Add `--apply` to launch it.

Progress goes to stderr. Top-level `--help` lists the commands and exits 0.
The argument parser reports rejected invocations on stderr and exits 2.

`incomplete` means a reported result other than completion or interruption. `json_object` means one JSON object on stdout.

```python cli
declare_cli_contract(
    interface='release',
    action='dispatch_framework_release',
    exit_codes={'completed': 0, 'incomplete': 1, 'interrupted': 130},
    stdout='json_object',
)
```
