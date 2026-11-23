---
atom_family: SPEC
atom_id: AN-S-2776
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Bind Carriers to their represented current or historical Entities

# Summary

Bind Carriers to their represented current or historical Entities

## Scope

Carrier bindings of non-ephemeral Entities.

## Claim

a Carrier binding **must** identify the Entity actually represented by that Carrier. a current Entity's Carrier binds that current Entity; a preserved historical state's Carrier binds that Revision. citing a current Entity's Version **must not** reclassify the current Entity as a historical Revision.

## Details

Use the separately defined CARRIES meaning. Its IS_CARRIED_BY inverse exposes the same binding with the endpoints reversed; neither direction substitutes a historical Revision for the current Entity actually represented. The applicable Carrier policy determines the representation. General representation rules may carry dependent properties inside one File Carrier; this policy does not require a separately registered binding for each field or section. It creates no additional Carrier, snapshot, Journal record or history gate.
