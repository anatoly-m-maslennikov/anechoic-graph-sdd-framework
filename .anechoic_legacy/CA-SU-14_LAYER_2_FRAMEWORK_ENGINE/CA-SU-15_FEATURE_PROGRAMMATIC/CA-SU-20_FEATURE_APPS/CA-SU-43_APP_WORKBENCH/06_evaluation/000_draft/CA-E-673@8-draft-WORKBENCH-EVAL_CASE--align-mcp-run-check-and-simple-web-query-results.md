---
identity:
  atom_id: CA-E-673
  ref_id: CA-E-673@8-draft
context:
  container:
    scope_unit: CA-SU-43
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development
      <+ Architecture <+ Communication <+ Interface Contracts
    dependencies:
    - MODEL//ANECHOIC <+ Projection
  tier: 5
relations:
  evaluation_for:
  - CA-R-2729
  - CA-R-2727
  - CA-D-673
  - CA-R-1603
  - CA-C-724
  IS_REPLACEMENT_FOR:
  - CA-E-673
state:
  status: draft
  version: 8
  updated_at: '2026-11-14T07:52:52.827355+00:00'
destination:
  file:
    name: CA-E-673@8-draft-WORKBENCH-EVAL_CASE--align-mcp-run-check-and-simple-web-query-results.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/06_evaluation/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH
author: Anatoly Maslennikov
---
## Summary

Align MCP Run, Check, and simple web query results

## Claim

### Prose Claim

Verify MCP and web Run, Page, and Check return equivalent results through
the same synchronous query capability.

## Details

- Compare complete default exports and explicit inline pages. Preserve
  ordered duplicate columns, Unicode, exact counts, and positional values.
- A Run executes once. After source refresh, its query ID still returns
  the same pages. A new Run reads refreshed data.
- Check returns validation metadata and available exact counts. It returns
  no rows or file and creates no save or log entry. Responses omit SQL echoes.
- Invalid SQL, size, offset, or query ID returns a useful error without retry.
- Exercise both adapters with the optional UI absent, and check the production
  web editor, errors, counts, and paging through the Python listener.
- Verify that the frontend fetches one page at a time and uses shared controls.
- Source errors report their path to stderr. Unrelated valid data stays queryable.
