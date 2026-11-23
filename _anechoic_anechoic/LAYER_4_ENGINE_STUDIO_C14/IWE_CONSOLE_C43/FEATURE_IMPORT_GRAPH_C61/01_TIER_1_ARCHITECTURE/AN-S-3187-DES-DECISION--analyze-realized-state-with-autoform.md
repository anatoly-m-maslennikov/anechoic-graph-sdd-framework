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
  IS_SOLUTION_FOR:
  - AN-S-3182@11
state:
  status: active
  version: 1
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Analyze realized state with Autoform

## Claim

### Prose Claim

Reuse Realization Graph ownership, Code Unit IDs, calls, and source
locations. Lower supported Python, JavaScript, and TypeScript paths to
ordered Lean cases. Use Autoform and runtime post-state comparisons for
representative paths.

Check private and shared reads and writes against the owner's policy.
Follow supported reached zero-argument calls and check each callee under
its policy. Count a return when it reaches the Action boundary. Count
writes that restore the starting value.

Report an undeclared silent path when a concrete input reaches an Action
with zero tracked writes and zero observable output. Publish evidence in
`state_effect_findings`. Mark missing or unsupported evidence unresolved.
Enforce findings only after the language passes the runtime comparison.
