---
atom_family: SPEC
atom_id: AN-S-2249
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-06 20:37:19 +0400
---

## Summary

Write Workbench SQL queries in the established style

## Claim scope

SQL queries written for Workbench and its child Scope Units.

## Claim

### Prose Claim

Write Workbench SQL queries in this style:

```sql
SELECT
  "content.claim.prose_claim"
  ,"content.claim.formal_claim"
from atoms
where true
  and "header_status" = 'Active'
  and "content.claim.formal_claim" is not null
;
```

Use uppercase `SELECT` on its own line. Indent selected columns and conditions by two spaces; put each additional selected column on its own line with a leading comma. Use lowercase `from`, `where`, `and`, and other SQL keywords. Start a filtered `where` clause with `true`, then put one condition on each following line. Double-quote identifiers and single-quote string values. Put the final semicolon on its own line.

Use the actual complete flattened Header names and the declared Content names with dotted snake_case segments.
