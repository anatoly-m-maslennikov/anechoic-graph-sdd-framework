---
atom_family: SPEC
atom_id: AN-S-2249
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T20:50:54.635724+00:00'
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
  and "header.state.status" = 'Active'
  and "content.claim.formal_claim" is not null
;
```

Put uppercase `SELECT` on its own line. Indent selected columns and conditions by two spaces. Put each additional selected column on its own line with a leading comma. Use lowercase `from`, `where`, `and` and other SQL keywords. Start a filtered `where` clause with `true`; put each condition on a following line. Double-quote column names and single-quote string values. Put the final semicolon on its own line.

Use complete Header and declared Content paths, with dots between levels and snake_case within each segment.

When formatting existing SQL, retain its expressions, identifiers, literal values and comments. Apply layout and keyword case without adding clauses, conditions or identifier quotes to reproduce an example.
