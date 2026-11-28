---
atom_family: SPEC
atom_id: AN-S-1925
container:
  component: C14
tier: 3
context:
  lens: SWD
state:
  status: "active"
  version: 2
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---
## Summary

Execute Workflow business logic in Python

## Claim

### Prose Claim

Author executable business logic and Action order in one Python entry point in the Workflow Atom's Formal Claim. Use descriptive names and named parameters. Bind each Action call to a declared Step and Action.

Run reviewed Python from an admitted Workflow revision with typed invocation input and the read data it needs through the Engine interface. Keep effectful I/O in Actions. Derive any execution diagram from the same Workflow logic.

Before dispatch, the Engine binds the Project and the exact Workflow, Step, and Action revisions. It validates invocation input, invokes Actions, and accumulates outcomes and effects.

Actions call adapters and recheck the input and source revisions they act on. On Action failure, stop further dispatch and return the failure and recorded effects.

Follow the Engine access-channel rules in AN-S-5188.
