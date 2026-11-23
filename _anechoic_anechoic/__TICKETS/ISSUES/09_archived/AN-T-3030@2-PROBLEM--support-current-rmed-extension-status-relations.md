---
atom_family: TKT
atom_id: AN-T-3030
container:
  component: C15
priority: 2
context:
  template: problem
state:
  status: archived
  version: 2
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Support Current RMED extension-status relations

# Summary

Support Current RMED extension-status relations

## Concern

R1676v21 changes RMED relation eligibility from Active to Current. Core RMED domains currently contain only Draft/Active/Archived, so current Core behavior is unchanged, but an admitted extension-specific non-Active Current RMED status would encounter the legacy Active-only inventory/graph logic.

## Evidences

Read-only source and caller comparison verified the Core domain equivalence. No current RMED extension-specific Status declaration was found. The latent gap spans _resolve(active_rmed), _rmed_status and ordinary proposed-reference inventory. This is an extension capability gap, not a reproduced Core failure or proof of current production data loss.

## Blast radius

Schedule one source-bound qualified-status implementation covering all three boundaries and frozen extension cases; changing only a string comparison would omit model/reference safeguards. Do not claim general extension Current-status relation acceptance from the present Core proof.
