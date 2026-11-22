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
  version: 2
  updated_at: "2026-11-22T02:18:13.895019+00:00"
---
## Summary

Read guarded filesystem inputs

## Guarantee

Open admitted filesystem paths without following symbolic links. A bounded read checks its declared roots and read limits, refuses protected paths, and records input fingerprints. A caller can check whether its recorded inputs still match the filesystem.

Parse UTF-8 YAML frontmatter within fixed syntax limits. Refuse aliases,
merge keys, duplicate keys, and non-string mapping keys. Return header
data and body text for the caller to interpret.

## References

AN-S-3069 and AN-T-2944.
