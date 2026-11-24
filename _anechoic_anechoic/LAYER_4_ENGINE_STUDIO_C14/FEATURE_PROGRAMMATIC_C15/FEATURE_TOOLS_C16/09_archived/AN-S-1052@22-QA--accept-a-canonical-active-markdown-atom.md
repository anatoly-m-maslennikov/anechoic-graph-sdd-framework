---
atom_family: SPEC
atom_id: AN-S-1052
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Accept a canonical active Markdown Atom

# Accept a canonical active Markdown Atom

## Test case

**Fixture:** validate one canonical active Markdown Atom with a registered address, minimal frontmatter, one matching H1, **and** a non-empty claim body.

**Expected result:** pass with exit `0`, an empty diagnostic set, **and** unchanged bytes.
