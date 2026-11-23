---
atom_family: SPEC
atom_id: AN-S-2421
container:
  component: C18
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Upgrade active Atom authority

# Summary

Upgrade active Atom authority

## Scope

Independently admitted upgrades of active Atom authority under the applicable Tier and Scope Unit rules.

## Claim

the `ATOM_UPGRADE` Tool is the canonical Doer for upgrading active ANECHOIC Markdown Atoms **to** an explicit operator-supplied enabled target Tier of `core` **or** `standard` that is higher than the source Tier. upgrade is neither archive nor promotion: it preserves the stable Atom ID **and** **may** keep the current Scope Unit **or** move the Atom **only** **to** an explicitly named ancestor Scope Unit. the Tool **must** derive the target authority location **and** filename scope segment **when** the Scope Unit changes, advance revision metadata, **and** reject missing, disabled, non-higher, **or** other invalid target Tiers, non-active Atoms, non-ancestor Scope Units, identity **or** destination collisions, **and** partial operations. each Action upgrades **`=1`** explicit Atom target with its expected Revision or digest. A several-Atom Workflow stops at its first failed Action, retains completed upgrades and leaves the remaining targets untouched, while preserving each Action's own preconditions and storage-effect safeguards. it **must** default **to** a mutation-free dry run **and** accept `--apply` **only** through an authorized project-local MCP delegation with a sealed Initiative action envelope.

## Details
