---
atom_family: SPEC
atom_id: AN-S-2455
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Validate required defaults and optional overrides

# Summary

Validate required defaults and optional overrides

## Claim

the Carrier validation Tool **must** preserve the distinction between a required defaulted Atom value **and** an optional inherited-setting override under CA-D-485.

- accept a required internally carried value equal **to** its registered default; reject its omission rather than rejecting its presence as redundant.
- accept an unselected absent override **and** a selected explicit override that currently equals the inherited value; change the upstream setting **and** verify that **only** the unselected override follows inheritance.
- reject the same Property maintained independently **in** frontmatter **and** body.
- a CLI failure identifies the Property **and** violated encoding rule with a non-zero exit **without** rewriting source values.
