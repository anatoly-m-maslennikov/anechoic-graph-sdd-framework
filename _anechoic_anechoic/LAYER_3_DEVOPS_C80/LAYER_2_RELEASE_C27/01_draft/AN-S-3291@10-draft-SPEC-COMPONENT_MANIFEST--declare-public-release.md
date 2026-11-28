---
atom_family: SPEC
atom_id: AN-S-3291
container:
  component: C27
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 10
  updated_at: "2026-11-26T15:52:25.464631+00:00"
---

## Summary

Declare Public Release

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C64',
        name='Public Release',
        layer=3,
        lens_whitelist=['DevOps'],
    ),
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['C64']},
          'exports': {'LAYER_3_PUBLIC_RELEASE_C64__shared.PublicReleaseError': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_3_PUBLIC_RELEASE_C64/LAYER_3_PUBLIC_RELEASE_C64__tests']},
                      'LAYER_3_PUBLIC_RELEASE_C64__shared.run_public_release': {'private': ['parent',
                                                                                            'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_3_PUBLIC_RELEASE_C64/LAYER_3_PUBLIC_RELEASE_C64__tests']}}},
 'io': {'server': {'public_release': {'transport': 'cli',
                                      'runner': 'uv',
                                      'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                                      'command': 'public'}},
        'client': []},
 'state': {'reads': ['Git commits and completed Task and Epic Markdown',
                     'Public release content draft'],
           'writes': []}}
```

## Component Contract

### Run Public Release from the command line

#### Guarantee

From the Framework checkout, run `./release__public public --run-id <id>`.
Use `--project-root <path>` to select a Project checkout. The defaults are
`--base origin/main` and `--head amm/dev`.

C64 imports no Project code outside the Release subtree and calls no subsystem. It reads Git directly through the host operating-system interface.

It selects changed, completed Task and Epic Markdown at the pinned head and returns that evidence, the commit pins, and a Luna diff-review handoff.

A second invocation supplies `--content-draft <file>` as UTF-8 JSON with `base_commit`, `head_commit`, and `changes`. Each change has `title`, `details`, `evidence`, and `highlight`.

The commit pins must match the comparison. Mark one to five changes as highlights for short Version History bullets.

The JSON result carries the detailed Local Release change record as the pull request description and a brief Version History draft. C64 does not publish externally or write those drafts to the checkout.

Progress goes to stderr. Exit 0 means completed. Exit 1 means another
reported outcome, including the evidence handoff. The argument parser
refuses invalid CLI usage with exit 2. If the host invocation catches an
interruption, it reports a failed JSON outcome and exits 130. Publication
remains the Operator’s responsibility.

#### References

AN-S-3291@6.

```python cli
declare_cli_contract(
    interface='public_release',
    action='prepare_public_release',
    command='public',
    effects={
        'resolve_git_pins': ('git_base_head', 'resolved'),
        'read_ticket_evidence': ('ticket_evidence', 'read'),
    },
    cases={
        'completed': {'must_effect': ('resolve_git_pins',)},
        'input_required': {
            'must_effect': ('resolve_git_pins', 'read_ticket_evidence'),
            'must_precede': (('resolve_git_pins', 'read_ticket_evidence'),),
        },
        'failed': {},
    },
    invariant={'forbid_effect': ('external_publish', 'checkout_write')},
)
```
