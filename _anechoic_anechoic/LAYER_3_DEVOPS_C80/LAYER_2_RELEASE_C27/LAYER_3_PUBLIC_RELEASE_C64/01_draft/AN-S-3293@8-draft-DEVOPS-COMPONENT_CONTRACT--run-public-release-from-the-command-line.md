---
atom_family: SPEC
atom_id: AN-S-3293
container:
  component: C64
tier: 0
context:
  template: component_contract
  lens: DevOps
relations:
  ANSWERS:
  - AN-S-3291
state:
  status: draft
  version: 8
  updated_at: '2026-11-25T00:00:00+00:00'
---
## Summary

Run Public Release from the command line

## Guarantee

From the Framework checkout, append `public --run-id <id>` to the host `uv` command in AN-S-3288. Use `--project-root <path>` to select a Project checkout. The defaults are `--base origin/main` and `--head amm/dev`; those options select other Git refs.

C64 imports no Project code outside the Release subtree and calls no subsystem. It reads Git directly through the host operating-system interface.

It selects changed, completed Task and Epic Markdown at the pinned head and returns that evidence, the commit pins, and a Luna diff-review handoff.

A second invocation supplies `--content-draft <file>` as UTF-8 JSON with `base_commit`, `head_commit`, and `changes`. Each change has `title`, `details`, `evidence`, and `highlight`.

The commit pins must match the comparison. Mark one to five changes as highlights for short Version History bullets.

The JSON result carries the detailed Local Release change record as the pull request description and a brief Version History draft. C64 does not publish externally or write those drafts to the checkout.

Progress goes to stderr. The evidence handoff is an input-required outcome.

## Claim

### Prose Claim

Exit 1 covers both a request for input and a failure.

### Formal Claim

```python cli
declare_cli_contract(
    interface='public_release',
    action='prepare_public_release',
    runner='uv',
    path='LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
    command='public',
    exit_codes={'completed': 0, 'input_required': 1, 'failed': 1, 'invalid_usage': 2, 'interrupted': 130},
    output='completed',
    must_effect=(('git_base_head', 'resolved'), ('content_draft_commit_pins', 'matched'), ('release_drafts', 'rendered'), ('pull_request_description', 'returned'), ('version_history', 'returned')),
    must_precede=((('git_base_head', 'resolved'), ('content_draft_commit_pins', 'matched')), (('content_draft_commit_pins', 'matched'), ('release_drafts', 'rendered')), (('release_drafts', 'rendered'), ('pull_request_description', 'returned')), (('content_draft_commit_pins', 'matched'), ('version_history', 'returned'))),
    forbid_effect=('external_publish', 'checkout_write'),
)
```
