---
atom_family: SPEC
atom_id: AN-S-3187
structure:
  container:
    component: C61
  tier: 1
context:
  lens: DES
  template: DECISION
relations:
  REFERENCES:
  - AN-S-2780@25
  - AN-S-3083@4
  - AN-T-2952
state:
  status: draft
  version: 1
  updated_at: '2026-11-21T16:47:20.457433+00:00'
---

## Summary

Analyze realized state with Autoform

## Claim

### Prose Claim

Extend the Realization Graph with a State Analyzer. Use Autoform to translate
selected Modules into a shared Lean model. Reuse graph identities and the
existing source watcher. Keep source locations on observations.

Evaluate reads and writes against the authored state boundary. Store findings
with their source locations in the existing DuckDB projection. Workbench,
Console, MCP, and lint use the same findings.

Pilot Python and JavaScript. Compare each language's observed post-state with
its runtime before using its findings to block lint. Report incomplete
analysis as unresolved.
