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
  updated_at: '2026-11-21T16:47:20.457433+00:00'
---

## Summary

Analyze realized state with Autoform

## Claim

### Prose Claim

Extend the Realization Graph with a State Analyzer. Use Autoform to translate
selected Modules into a shared Lean model. Reuse graph identities and the
existing source watcher. Keep source locations on observations.

Evaluate reads and writes against the authored state boundary. A reachable
action with zero writes and zero observable outputs is a dead end unless
declared as a no-op. Publish findings through the existing DuckDB projection.

Pilot Python and JavaScript. Compare the ordered effects, outcome, and
post-state with the runtime. Block lint only with confirmed evidence.
Report incomplete analysis as unresolved.
