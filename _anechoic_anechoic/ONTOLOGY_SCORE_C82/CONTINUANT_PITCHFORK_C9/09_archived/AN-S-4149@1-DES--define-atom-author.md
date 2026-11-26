---
atom_family: SPEC
atom_id: AN-S-4149
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Atom Author

## Claim scope

The resolved author of an Atom Revision.

## Claim

Atom Author is the resolved author of one Atom Revision and has exactly one string value. If no explicit author is supplied, the admitting Operator is the effective Author; Markdown Delivery serializes the resolved nonempty registry name in frontmatter.

### Formal claim

```text
Atom.Author[string]{1}
```

## Details

Source meaning: CA-R-655, CA-R-1078, CA-R-1080, CA-D-274. Scope-specific constraints remain in their governing Rs.
