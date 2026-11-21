---
atom_family: TKT
atom_id: AN-T-372
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: canceled
  version: 3
  updated_at: 2026-10-24 06:26:31 +0400
---
## Summary

Remove derivable frontmatter


# Remove derivable frontmatter

1. [ ] Ditch the default priority (`medium`).
2. [x] Ditch types in frontmatter; they are already in the filename.
3. [x] Consider deleting `scope_path` from frontmatter; it can also be derived from where the file sits.
