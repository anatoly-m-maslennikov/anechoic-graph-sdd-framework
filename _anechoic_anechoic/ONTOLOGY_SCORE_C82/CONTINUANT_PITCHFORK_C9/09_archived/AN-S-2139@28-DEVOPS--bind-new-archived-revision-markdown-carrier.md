---
atom_family: SPEC
atom_id: AN-S-2139
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 28
  updated_at: '2026-11-11T19:34:00+04:00'
---
## Summary

Bind new archived Revision Markdown Carrier

## Claim

### Prose Claim


The single Markdown Archive Carrier created for an Atom Revision newly placed in Archived status.


Place Archived Atom Markdown Carriers in the shared `<owning scope unit>/<role folder>/<status folder>/` directory. The Atom's owning Scope Unit and Role determine this directory.

When an Atom Revision attains Archived Status, classify its single Markdown Archive Carrier as that Revision's Archive Carrier. Its filename is `<canonical-ID>@<version>[-<remaining-filename-components>].md`. The single `@<version>` marker occupies the Atom-ID segment under CA-D-283/CA-D-289. Preserve the archived Atom's numeric Version and prior Updated At; its new Archive Carrier carries logical Archived Status encoded as `archived` through the common named-value rule.

### Formal Claim

```CFEL
# model
Atom/(.Header.State.Status := Archived).Header.Destination.File.Path == PATH_TEMPLATE("<owning scope unit>/<role folder>/<status folder>");
```

## Details

This rule applies to newly archived Revisions. It does not relocate existing historical carriers or authorize independent legacy moves, rewrites, or automatic normalization of legacy filenames.
