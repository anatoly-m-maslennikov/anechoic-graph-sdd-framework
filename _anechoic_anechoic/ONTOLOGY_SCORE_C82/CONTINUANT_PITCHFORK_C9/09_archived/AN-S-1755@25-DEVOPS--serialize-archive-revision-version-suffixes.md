---
atom_family: SPEC
atom_id: AN-S-1755
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 25
  updated_at: "2026-11-25T20:14:08.966071+00:00"
---
## Summary

Serialize Archive Revision Version Suffixes

## Claim

### Prose Claim


Archive Carrier basenames for Archived Atom versions.


**every** Archived Atom Carrier basename **must** serialize the archived Atom's canonical ID with exactly one `@<version>` marker, where `<version>` is the unchanged numeric Version Number of that Archived Atom version. The marker **must** occur in the filename's Atom-ID segment under CA-D-283; do **not** append a second `@<version>` to a basename that already carries the marker. Existing legacy archive basenames are not normalized automatically.
