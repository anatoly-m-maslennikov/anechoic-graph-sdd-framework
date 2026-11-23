---
atom_family: SPEC
atom_id: AN-S-2250
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Derive the query Projection only from governed Atom sources

## Claim scope

The query Projection of canonical Current and Draft Atom carriers in the governed source inventory.

## Claim

### Prose Claim

The query Projection **must**:

- derive its data only from canonical Current and Draft Atom carriers in the governed source inventory; Archived carriers are excluded.
- retain each indexed carrier's source locator, Atom identity, Version, lifecycle group, parsed Header, Markdown Content, and mapped Content Properties.
- make each source-derived Projection row include a hash for that row's complete Projection data.
- include every Current carrier regardless of its status, including Done and Canceled, and keep Current and Draft groups distinct. A carrier in one group **must not** overwrite a carrier in another group solely because they share a base ID.
- derive current Scope Unit structure only from Current Scope Unit Declarations. Draft Declarations remain queryable Atoms but do not establish Current structure. Parse source YAML and Markdown directly; no Declaration-to-reader-schema compiler is required.
- treat an observed Atom identity and Version as source data, not as a fixed-file pin or proof of a Journal record.
- remain derived data that can be rebuilt from its sources.
- never edit, move, archive, promote, or invent a source Atom.
