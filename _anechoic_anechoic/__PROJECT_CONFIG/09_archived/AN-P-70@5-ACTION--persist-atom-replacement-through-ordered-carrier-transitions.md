---
atom_family: PROJECT_CONFIG
atom_id: AN-P-70
structure:
  container:
    component: C9
context:
  template: action
state:
  status: archived
  version: 5
  updated_at: 2026-09-28 06:30:40 +0400
---
## Summary

Persist Atom replacement through ordered Carrier transitions

# Persist Atom replacement through ordered Carrier transitions

Persist Atom Replacement **means** the reusable Action that persists **`=1`** accepted Atom replacement through its successor activation **and** predecessor archival under CA-R-1432 **and** CA-R-807. its boundary is this replacement transition; it does **not** select **or** authorize the replacement. the execution **must** perform **all** of:

1. persist the successor as Active **before** archiving the predecessor.
2. archive the predecessor as one whole Carrier under CA-D-303 **and** record the corresponding replacement **in** the authoritative Journal with explicit predecessor **and** successor Atom IDs under CA-R-807.
3. preserve the predecessor's content, identity, frontmatter, **and** Version exactly; change its basename **only** by adding the canonical `@<version>` Archive suffix under CA-D-289.
4. keep replacement history out of predecessor **and** successor Atom frontmatter; formal replacement relations **and** inverse navigation remain deferred under CA-R-807.
