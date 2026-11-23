---
atom_family: SPEC
atom_id: AN-S-2374
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 4
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Execute one snapshot-stable Artifact query

# Summary

Execute one snapshot-stable Artifact query

## Scope

The query evaluation method for FIND_AND_FETCH_ARTIFACTS, not a new parser,
Workflow, or Journal.

## Claim

FIND_AND_FETCH_ARTIFACTS **must** have CA-O-159 enumerate and retain one
allowlisted Markdown snapshot before parsing the closed filter grammar, then
evaluate and paginate only that retained snapshot in canonical identity order.

## Details

Reuse the existing safe Markdown/frontmatter parser. Validate the full snapshot
before accepting a result; preserve per-carrier diagnostics and reject ambiguity
or incomplete reads. Apply
CA-R-1850 without delegation to SQL, code, or eval; retain distinct
frontmatter/section namespaces and generic identity policy. Fetch bodies only
after matching identity and explicit selected request. Bind cursors to retained
digest and exact retained members; continuation cannot enumerate again. Enforce
resolved budgets and return measured coverage. No helper writes carriers,
Projections, Runs, or Journal Events on its own. An actual admitted selected
Action/Workflow uses CA-D-527 through CA-D-529 for shared Run and Journal
recording.
