---
identity:
  atom_id: AN-P-47
context:
  container:
    component: C27
  tier: 3
  template: action
state:
  status: active
  version: 15
  updated_at: 2026-11-09 15:54:30 +0400
---

# Summary

Aggregate the full Release Gate

## Action

Aggregate the full Release Gate **means** the read-only decision over the exact closed-unit, image-canary and host Candidate E2E receipts for one frozen N/N+1 candidate.

## Details

Every receipt must name the same candidate manifest, source frontier, compiled output, package, immutable image and parent lineage. The Unit receipt must cover every declared testcase outside the current `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/tests/` host-capable runtime-test set; the E2E receipt must cover every testcase in that set. Every declared testcase must terminal-pass: skipped, excluded, missing or zero-coverage testcase is non-pass. Missing, stale, mixed-candidate, partial or unjournalable evidence is non-pass. This Action creates no runtime/Skill selection, image removal, retry, Docker effect or new authority.
