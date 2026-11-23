---
atom_family: SPEC
atom_id: AN-S-3293
container:
  component: C64
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3291
state:
  status: "active"
  version: 5
  updated_at: "2026-11-23T01:48:06.194711+00:00"
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

Progress goes to stderr. Exit 0 means completed. Exit 1 means another reported outcome, including the evidence handoff. Exit 2 means invalid CLI usage. Exit 130 means interruption.

## References

AN-S-3291@2.
