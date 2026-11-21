---
atom_family: TKT
atom_id: AN-T-272
structure:
  container:
    component: C00
  priority: 2
context:
  template: task
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Bind the public graph notation profile

## Objective

The existing public graph entry point uses an explicit approved profile under the accepted contracts.

## Details

Estimated own work: 15 minutes. Assignee: AI Agent. Required prerequisites: CA-P-2169 and its actual current public graph contract packet independently accepted under CA-P-2171. Other contract packets need not be complete. Reopen public graph callers/exports/fixtures and bind the affected entry-point files. Own public profile forwarding/validation and its focused tests; reuse the internal reviewed parser and coordinate shared files with integration.

Apply the smallest change that carries and validates the selected approved profile through the existing path. Check approved compact/selector forms, `Atom`/`atom` case, unsupported/absent explicit selection, legacy/default behavior, pins and provenance. Do not add native Relations or infer meanings from candidate display paths. Deliver code/test pins and actual results to CA-P-2174. Split larger work before execution. No production graph or Core source change occurs.

### Completion receipt

The actual public graph contract packet passed [independent contract acceptance](../../../../_projection/core-entity-review/stage2/tools-first/contract-acceptance.md) before implementation. Commit `a8da9b50b` implements the explicit approved profile in the existing request/entry-point/source path and adds its focused public-profile checks. `tools_first_verifier` independently accepted the bounded implementation. Root ran 245 graph checks and four MCP descriptor checks; all passed. Legacy/default behavior, case distinctions, grammar/source pins and publication/no-op safeguards remain covered; parsing grants no native fact admission or selector resolution.

This completes CA-P-2176 only. Preview-fix acceptance, the combined CA-P-2174 Tool receipt, admitted application implementation and live migration gates remain separate. No Core source or runtime publication effect is claimed.

### Definition of Done

The Plan is **not** Done if contract acceptance is missing/stale, a caller silently uses the wrong profile, legacy/case/source semantics regress, native admission is inferred, focused checks fail, or own work exceeds 15 minutes without decomposition.
