---
atom_id: CA-D-507
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Active
version: 16
updated_at: 2026-11-02 00:18:22 +0400
subjects:
  active: ANECHOIC_MODEL <+ Entity
  passive:
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Carrier.Format
  - ANECHOIC_MODEL <+ Carrier/File.Extension
relations: {}
tier: 1
role: Delivery
form: Decision
---
## Summary

Separate Entity identity from Carrier format

## Claim

### Prose Claim


changes limited **to** Carrier Format **or** File Carrier Extension.


a change **to** Carrier Format **or** File Carrier Extension alone **must not** establish **or** change Entity identity.
