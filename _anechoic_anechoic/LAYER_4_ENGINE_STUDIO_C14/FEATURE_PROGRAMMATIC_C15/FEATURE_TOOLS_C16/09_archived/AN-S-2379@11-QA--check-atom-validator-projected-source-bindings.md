---
atom_family: SPEC
atom_id: AN-S-2379
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Check Atom validator projected-source bindings

# Summary

Check Atom validator projected-source bindings

## Scope

`VALIDATE_ATOMS` projected-Carrier source bindings.

## Claim

the `VALIDATE_ATOMS` projected-Carrier check **must** implement CA-D-305-CORE_META_MODEL-CORE-DELIVERY--carry-projected-atoms-without-new-identity source binding faithfully.

- accept a valid relative binding **to** the selected original source Atom **when** identity, Revision, **and** authored bytes match.
- reject missing, ambiguous, wrong-source, stale, **or** out-of-bound bindings, modified Claims, **and** generated Projection metadata placed on an authoritative source Atom.
- resolve the relative path from the projected file's directory; include nested output fixtures.
- remove **only** the admitted generated binding for byte comparison. preserve **all** source Properties **and** body content; do **not** strip arbitrary extra metadata **to** obtain a match.
- preserve the one-way Projection-to-source binding **without** inventing a second Atom identity **or** demanding an inverse link on the source.

## Details
