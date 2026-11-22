---
atom_family: SPEC
atom_id: AN-S-1225
container:
  component: C27
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 16
  updated_at: '2026-11-21T21:49:04.407565+00:00'
---

## Summary

store Release host state in an isolated namespace

## Claim

### Prose Claim

the direct host release implementation's mutable delivery artifacts **must** remain below the resolved Project root in `.anechoic_runtime/` or `.anechoic_tmp/`, separate from authoring sources and Docker/MCP runtime state.

## Details

### Scope

the Local and Public Release artifacts written by the direct host implementation.

- Local Release writes its installed runtime package and reports below `.anechoic_runtime/simple_local_release/` and uses `.anechoic_tmp/simple_local_release/` only for temporary staging and test output.
- Public Release returns pinned Git evidence and draft text without writing release artifacts.
- all locations are derived from the resolved Project root and must remain project-relative. They do not create a Workflow Orchestrator namespace, scheduler database, worker lock, Queue, DBOS store or private IPC carrier.
- reports and temporary artifacts describe delivery results; they do not become authoring authority or a second Journal.
- the Docker/MCP runtime remains independently packaged and managed by the release implementation.
