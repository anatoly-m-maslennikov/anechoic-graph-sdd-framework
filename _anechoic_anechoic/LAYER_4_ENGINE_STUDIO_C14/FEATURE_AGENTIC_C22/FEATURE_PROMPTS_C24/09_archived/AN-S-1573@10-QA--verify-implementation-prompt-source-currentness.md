---
atom_family: SPEC
atom_id: AN-S-1573
container:
  component: C24
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Verify implementation prompt source currentness

# Summary

Verify implementation prompt source currentness

## Scope

the source-binding frontier for all seven Implementation Workflow prompts.

## Claim

the Implementation passes this Evaluation only when each required source identity, version, path, and digest matches current fully reviewed authority.

## Details

The stale delivered O016v9 and old Step/Action pins fail this case until an independent PROMPTS review has refreshed them; a digest edit alone is not a pass.

The Evaluation also fails when a packet resolves the reviewed source rows from
an immutable prompt-code root, ambient current directory, host-path guess, or
unbound mount rather than its `selected_project` binding. It fails when a
source reference is absolute, escapes `.anechoic_anechoic`, has a duplicate,
missing, stale, or mismatched identity/version/digest, or when the active-M
Projection is not verified against the same selected Project source frontier.
An Agent must not launch in those cases. If a packet declares executable work,
the Evaluation also requires the existing explicit `workspace` and the exact
matching `permissions.implementation_workspace` capability; their absence or
mismatch is blocked evidence, not a new permission or a successful mock run.
