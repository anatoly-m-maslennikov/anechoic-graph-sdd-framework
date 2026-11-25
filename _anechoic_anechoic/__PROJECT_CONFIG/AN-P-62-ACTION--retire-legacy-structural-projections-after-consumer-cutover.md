---
atom_family: PROJECT_CONFIG
atom_id: AN-P-62
structure:
  container:
    component: C9
context:
  template: action
state:
  status: "active"
  version: 15
  updated_at: "2026-11-25T20:14:08.537042+00:00"
---
## Summary

Retire legacy structural Projections after consumer cutover

# Retire legacy structural Projections after consumer cutover

Retire Legacy Structural Projections **means** the Action that retires the obsolete Project Scope Unit Graph Sources Projection **or** Project Scope Unit Graph Projection **after** validated direct-consumer cutover.

- the selected target is a legacy Projection retained under archived AN-S-513@20 or AN-S-514@20, **not** authoritative Project Structure.
- retire that target **only** **after** its direct-consumer cutover is validated; an unresolved cutover does **not** satisfy this condition.
- preserve its recorded migration disposition **and** return the actual retirement result. this Action does **not** require rebuilding **or** refreshing the obsolete Projection **or** reintroducing consumer dependence.

this Action governs the retirement job **only**; it does **not** grant new mutation authority **or** prescribe the Tool implementation that performs it.
