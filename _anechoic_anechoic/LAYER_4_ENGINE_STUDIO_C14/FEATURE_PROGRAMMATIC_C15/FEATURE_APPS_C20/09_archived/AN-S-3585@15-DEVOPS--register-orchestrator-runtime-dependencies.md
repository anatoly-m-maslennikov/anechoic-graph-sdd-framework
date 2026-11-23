---
atom_family: SPEC
atom_id: AN-S-3585
container:
  component: C20
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Register orchestrator runtime dependencies

## Claim

### Prose Claim

the WORKFLOW_ORCHESTRATOR runtime **must** declare its selected DBOS, Pydantic **and** PyYAML dependencies **in** the workflow-orchestrator dependency group.

## Details

### Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

- DBOS provides durable orchestration with a local SQLite backend.
- Pydantic admits strict JSON requests **and** Agent results; PyYAML supports safe Atom Carrier parsing.
- Codex CLI is a separately installed executable selected through the runner boundary; no Claude backend is implemented yet.
- versions are pinned **after** compatibility verification with the repository's supported Python series. runtime installation does **not** launch a worker **or** execute a Project Run.

### Conditional future AI-Agent execution

Agent-result parsing, mock-Agent scheduling and Agent dispatch, where mentioned above, apply only to separately admitted AI-Agent execution. The retained deterministic contract does not start or restore an Agent runtime.
