---
atom_family: TKT
atom_id: AN-T-603
structure:
  container:
    atom: AN-T-633
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: "canceled"
  version: 7
  updated_at: "2026-11-20T20:04:00.167188+00:00"
---
# Summary

Prove immutable image source and mount guards

## Objective

Within <=15 minutes, Run the current fresh-image no-host-Engine-mount and stale-source rejection tests through the actual declared host MCP driver.

## Details

Use image sha256:057792974dc2d81f84f99dee5535a44d5ee30513b03f6154381d99aa0bd558cd, declared dependency groups workflow-orchestrator and rmed-workflow-mcp, and separate disposable Runtime Projects. No host Engine mount, assertion relaxation, live CLI or permission bypass. Other independent batches are separate Tasks; coverage counts only the assigned cases.

## Saved frontier

The host driver could not start: the repository virtual environment contains no Python executable. Provisioning the declared groups also failed on distribution-cache directory rename with EPERM in the existing and fresh permitted temporary cache. These attempts stopped. The bundled runtime lacks MCP, PyYAML and DBOS. No actual-image case ran; image tag was unchanged. CA-C-449 preserves the blocker. Prepared harness source does not count as execution or completion.

## Definition of Done

The assigned current immutable-image cases have exact passing functional evidence, or remain unfinished with their precise protected blocker.
