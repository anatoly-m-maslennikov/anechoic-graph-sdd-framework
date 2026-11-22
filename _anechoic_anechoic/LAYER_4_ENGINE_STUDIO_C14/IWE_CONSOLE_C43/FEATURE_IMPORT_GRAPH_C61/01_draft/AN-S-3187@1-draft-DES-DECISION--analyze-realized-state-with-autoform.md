---
atom_family: SPEC
atom_id: AN-S-3187
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-2780@25
  - AN-S-3083@4
  - AN-T-2952
state:
  status: draft
  version: 1
  updated_at: '2026-11-22T16:44:45.347890+00:00'
---

## Summary

Analyze realized state with Autoform

## Claim

### Prose Claim

Extend the Realization Graph with a State Analyzer. Lower supported source paths to ordered Lean cases. Keep Autoform and runtime
comparisons for representative paths. Reuse graph identities and the source
watcher, and keep source locations on observations.

Evaluate reads and writes against the authored state boundary. A reachable
action with zero writes and zero observable outputs is a dead end unless
declared as a no-op. Publish findings through the existing DuckDB projection.

Analyze Python, JavaScript, and TypeScript. Publish evidence in
`state_effect_findings`. Block lint on confirmed denied access and witnessed
undeclared dead ends. Report unresolved cases when coverage or Lean is missing.
