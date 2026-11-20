---
atom_family: TKT
atom_id: AN-T-984
structure:
  container:
    atom: AN-T-986
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 6
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Map the canonical Docker test network cleanup lifetime

## Objective

Resolve the observed isolated Docker network gate failure without affecting the working MCP.

## Details

Read-only source/caller/test mapping: fixture setUp/tearDown/addCleanup/finally; DockerRuntime down/stop; suite interruption and imageowner lifetime. Identify how networks persist on startupfailure,success,interruption. Propose smallest shared-owner repair preserving productionresourceboundaries. No writes/tests/Docker/MCP/release/Git. Return exactfiles/lines and evidence, not speculative broadcleanup.

### Actual result and next boundary

No current normal-path network leak is proven: ordinary, selected and first-cut HTTP fixtures already call scoped Compose down on teardown/finally, including partial startup. Existing production stop intentionally retains state and must remain unchanged. A forced child-process kill can bypass finally; a separate potential launcher no-container startup cleanup gap is recorded as C567 for reproduction, not patched speculatively. Old unattributed empty networks are not attributed to today's code.
