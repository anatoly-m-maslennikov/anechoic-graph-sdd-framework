---
atom_family: TKT
atom_id: AN-T-909
structure:
  container:
    atom: AN-T-1664
  priority: 2
context:
  template: task
state:
  status: done
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Prepare the disposable Subject client and Concern identity fixture

## Objective

Record the bounded read-only/test preparation needed to isolate the approved double-slash Subject case and preserve the frozen Concern identity authority fixture.

## Details

Use the supported disposable test-client initialization path and retain the exact frozen Concern identity authority fixture for the selected isolated cases. Keep this preparation separate from production state, source publication, and runtime acceptance. The prior Subject-test `AttributeError` is a client-initialization diagnostic boundary, not a reproduced production failure. Runtime verification remains pending in P2439.

At most15minutes ownwork, split before extending. Preserve exact predecessors and concurrent edits. No production MCP/Docker/Git effects.

### Definition of Done

Read-only/test preparation is recorded: disposable Subject client initialization and the frozen Concern identity authority fixture are explicit and reproducible. This narrow DoD does not claim a runtime pass, production acceptance, or completion of P2439.

### Completion checkpoint

Accepted report covers the disposable Subject client initialization that previously surfaced `AttributeError` and the frozen Concern identity authority fixture. Runtime execution and P2439 verification remain pending; no runtime result is claimed.
