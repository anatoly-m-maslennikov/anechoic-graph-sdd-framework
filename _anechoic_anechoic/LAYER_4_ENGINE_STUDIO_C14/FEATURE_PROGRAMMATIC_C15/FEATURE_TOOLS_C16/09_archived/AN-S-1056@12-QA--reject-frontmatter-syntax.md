---
atom_family: SPEC
atom_id: AN-S-1056
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject frontmatter syntax

# Reject frontmatter syntax

## Test case

**Fixture:** replace valid frontmatter with syntactically invalid YAML.

**Expected result:** fail with the stable frontmatter-syntax diagnostic **and** a non-zero exit.
