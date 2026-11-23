---
atom_family: SPEC
atom_id: AN-S-3497
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Require a pinned admitted package source catalog

# Summary

Require a pinned admitted package source catalog

## Scope

the source identity proof carried by a reusable package.

## Claim

the INSTALL_TOOLS facade **must** seal every selected package source with an admitted immutable revision and digest, and an unknown revision **must** fail **before** package, image, selector or target effects.

## Details

The catalog binds Core, selected active Methodology source, declared support and any available optional extension/configuration. Mutable tags, blank revisions, duplicate identities, mismatched source digest or caller replacement catalog refuse. The catalog digest is re-bound in candidate, package, image proof and activation evidence.

For local Core, selected active Methodology and declared support snapshots, the exact content digest may serve as the immutable revision. Their internal validation record binds the parent Operator-commanded local release to that exact source snapshot. A digest identifies content; the retained validation establishes its binding. Optional extensions remain explicitly selected and validated.

Source validation occurs only inside the Operator-commanded local release. It is preparation, not a substitute for the one complete local suite before local release effects. Approving design, preparing sources, or completing validation does not start a separately executable source-admission operation or another release.
