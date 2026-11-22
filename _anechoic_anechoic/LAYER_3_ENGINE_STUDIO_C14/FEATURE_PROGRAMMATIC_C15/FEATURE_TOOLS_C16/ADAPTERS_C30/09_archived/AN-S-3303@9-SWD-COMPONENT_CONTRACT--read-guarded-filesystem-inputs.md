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
  version: 9
  updated_at: "2026-11-22T03:28:25.363231+00:00"
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

Read native Headers and derive Carrier filenames and directories from
the supplied fields. Preserve the legacy filename grammar and reject
unsupported paths or contradictory fields.

Read authored Component Contracts and recognize legacy Scope Unit carriers.
Parse and render Subject notation with the selected grammar profile.

Read the legacy Project Settings selected for the current request.
Parse legacy Python Claims as literal calls and preserve their
Model or Instance grouping.

Read native Model Claims and Structure declarations without executing them.
Map realization paths to declared Component and Package owners. Retain
the source pins when discovering legacy Scope Unit declarations.

Capture Project carriers with their revisions, containment and source pins.
Report invalid sources and refuse a capture if the Manifest or carrier
inventory changes during the read. Decode Markdown headings and retain
the source ranges for declared Content properties.

## References

AN-S-3069 and AN-T-2944.
