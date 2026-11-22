---
atom_family: SPEC
atom_id: AN-S-425
container:
  component: C9
tier: 6
context:
  lens: QA
state:
  status: active
  version: 35
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Validate Authoritative Framework Settings Artifact

## Claim

### Prose Claim


Framework Instance Settings.


the Evaluation **must** reject Framework Instance Settings **if**

- it is treated as an Atom **or** Projection,
- has an Atom ID **or** Atom Content Role,
- resolves outside the current Project's registered instance directory,
- uses another Project's Settings Carrier,
- has other than **`=1`** authoritative TOML Carrier,
- **contains** Project initialization inputs **or** independently editable Project Structure,
- violates its foundational content boundary, applicable shared settings specifications, **or** applicable concrete field specifications **after** parameter resolution governed by CA-M-279,
- **or** lacks an exact current Revision, SHA-256 Digest, **and** Work Journal receipt admitted by CA-D-360.

## Details

for recovered baseline registration, the Evaluation **must** check the exact selected Project, Carrier path, lineage-derived logical Revision, **and** Digest binding required by CA-D-360. verify that registration leaves Settings bytes unchanged **and** records the actual observation time **and** evidence-backed observer Run **or** session. reject an absent **or** ambiguous binding, a stale Carrier Digest, a path-based Revision reset **or** guessed allocation, **or** a fabricated Settings write, past mutation, author, **or** history. an admitted baseline receipt **must not** replace any Settings schema **or** ownership check above **or** authorize another operation.
