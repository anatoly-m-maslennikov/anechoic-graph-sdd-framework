---
identity:
  atom_id: AN-T-2007
context:
  container:
    component: C45
  tier: 3
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Role-only Drafts disappear from the query index.

## Concern

The six lifecycle Drafts that carried the role-only technical reference
`CA-O-draft` shared one reference and were excluded from the derived source
inventory. A source-reader identity based only on the Atom ID could not retain
all of those carriers.

## Resolution

The SourceReader now preserves the `CA-O-draft` Atom ID and derives its
technical `ref` from the project-relative carrier path. The six real lifecycle
Drafts are verified, and one full-repository verification capture contained 4,908 Atoms,
47 Scopes, 30 role-only operation Drafts, and 30 unique references.
`tests/test_source_reader.py` passes 20 tests. This resolves the source defect;
runtime adoption and deployment remain separate tracking concerns.
