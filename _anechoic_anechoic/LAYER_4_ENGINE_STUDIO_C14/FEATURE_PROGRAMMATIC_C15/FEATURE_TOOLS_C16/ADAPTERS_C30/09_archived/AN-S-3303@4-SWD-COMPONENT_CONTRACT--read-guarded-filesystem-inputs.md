---
atom_family: SPEC
atom_id: AN-S-3303
container:
  component: C30
tier: 1
context:
  template: component_contract
  lens: SWD
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-22T02:36:18.087504+00:00"
---
## Summary

Read guarded filesystem inputs

## Guarantee

Open admitted filesystem paths without following symbolic links. A bounded read checks its declared roots and read limits, refuses protected paths, and records input fingerprints. A caller can check whether its recorded inputs still match the filesystem.

Parse UTF-8 YAML frontmatter within fixed syntax limits. Refuse aliases,
merge keys, duplicate keys, and non-string mapping keys. Return header
data and body text for the caller to interpret.

Read and write TOML settings carriers. Validate a replacement before
publishing it.

Append Journal rows to Project-local files in input order or stage them
for the database owner. Return receipts for completed appends. Report
partial completion when a batch stops.

Read grouped and historical Header fields without altering the carrier.
Reject conflicting aliases. Read legacy Atom identifiers and format
native exact revision references.

## References

AN-S-3069 and AN-T-2944.
