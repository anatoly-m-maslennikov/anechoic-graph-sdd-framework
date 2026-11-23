---
atom_family: SPEC
atom_id: AN-S-1987
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 23
  updated_at: 2026-11-11 17:36:58 +0400
---

## Summary

Delegate one Initiative-bound Atom mutation

## Claim

### Prose Claim

#### Atom Lifecycle Tools

Forward the operation and inputs to the bound Project runtime. If the runtime requests a correction, use an MCP form in the same call when the client supports it. Otherwise return the fields to correct. The next call in the same Project, client session and Tool may supply just those fields, plus any other corrections. Merge the corrections with the retained inputs and validate again before any effect. Return the backend outcome under CA-R-1105.

#### Initiative-bound procedure

Apply this procedure to Initiative-bound project-local Atom Tools.

1. Preserve the human-origin Initiative **and** select the one canonical Atom Tool **without** resolving its target **or** lifecycle meaning.
2. Forward the sealed request **to** that Tool **and** return its structured outcome unchanged.
3. Report success **only** **after** the canonical Tool returns its acknowledged outcome; preserve a rejection, conflict, partial result, **or** blocked result as such.

#### Outcome

The backend owns target selection, effects and verification. MCP forwards the request and reports the outcome.

#### Initiative-bound failure or stop

Stop and return an explicit failure if the Initiative, authorization, canonical Tool selection or Tool outcome is absent or invalid.
