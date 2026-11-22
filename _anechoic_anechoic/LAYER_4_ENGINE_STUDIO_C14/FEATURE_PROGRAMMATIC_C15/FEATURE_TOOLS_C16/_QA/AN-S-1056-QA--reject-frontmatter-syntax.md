---
atom_family: SPEC
atom_id: AN-S-1056
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject frontmatter syntax

# Reject frontmatter syntax

## Test case

**Fixture:** replace valid frontmatter with syntactically invalid YAML.

**Expected result:** fail with the stable frontmatter-syntax diagnostic **and** a non-zero exit.
