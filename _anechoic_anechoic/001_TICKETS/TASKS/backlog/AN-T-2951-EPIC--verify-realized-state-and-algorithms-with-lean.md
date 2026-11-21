---
atom_family: TKT
atom_id: AN-T-2951
container:
  component: C43
priority: 2
context:
  template: task
  label: Epic
state:
  status: backlog
  version: 2
  updated_at: '2026-11-21T16:34:17.093602+00:00'
---
## Summary

Verify realized state and algorithms with Lean

## Work

### Stage 1. Autoform state analysis

- Specify the State Analyzer first. Use Autoform to translate supported code into a shared Lean model. Use the existing Project source inventory, watcher, and DuckDB projection.
- Check reads, mutations, aliases, scope, and ownership across Module, Package, and Component boundaries. Apply `pure`, default `local`, and named channel grants `r`, `w`, and `rw` from the authored state boundary.
- Exercise a Ticket lifecycle transition in Python and a state mutation in JavaScript. Compare post-state with CPython and Node before enabling lint for each language.
- Publish findings with file, line, and the affected owner or channel. Workbench, Console, MCP, and lint use the same findings.

### Stage 2. PastaLean algorithm verification

- After the state analysis stage, use PastaLean to check selected Python algorithms against Spec properties. Start with transitive dependency selection for rebuild.

## Acceptance

- Fixtures cover a permitted local mutation, an alias that writes to shared state, and a write through a read-only grant.
- Record unsupported translation or missing post-state evidence as unresolved. Lint blocks confirmed violations.
- The algorithm check returns a checked property or a concrete counterexample. Open proof obligations stay visible.
