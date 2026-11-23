---
atom_family: SPEC
atom_id: AN-S-1056
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject frontmatter syntax

# Reject frontmatter syntax

## Test case

**Fixture:** replace valid frontmatter with syntactically invalid YAML.

**Expected result:** fail with the stable frontmatter-syntax diagnostic **and** a non-zero exit.
