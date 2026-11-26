---
atom_family: SPEC
atom_id: AN-S-1632
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T22:48:38.259510+00:00"
---

## Summary

Require work or decomposition in every Plan

## Claim

### Prose Claim


Plan Atoms other than Work Reports, their own work, and their direct Plan containment.


Every Plan Atom other than a Work Report **must** have **`>=1`** of:

- its own work content;
- **`>0`** outgoing derived `CONTAINS` links **to** directly contained Plan Atoms.

both contributions **may** be present within the same Claim; a Summary alone **without** either contribution is insufficient.
