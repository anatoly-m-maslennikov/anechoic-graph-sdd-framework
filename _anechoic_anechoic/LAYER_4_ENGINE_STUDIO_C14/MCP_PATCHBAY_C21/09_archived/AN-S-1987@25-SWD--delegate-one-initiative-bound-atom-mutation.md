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
  version: 25
  updated_at: '2026-11-12T08:41:09.794563+00:00'
---

## Summary

Delegate one Initiative-bound Atom mutation

## Claim

### Prose Claim

#### Atom Lifecycle Tools

Forward the operation and inputs to the bound Project runtime. If the runtime requests a correction, use an MCP form in the same call when the client supports it. Otherwise return the field errors and the fields to correct. The next call in the same Project, client session and Tool may supply just those fields or include other input fields. Merge the new inputs with the retained inputs and validate again before any effect. A call with only `cancel: true` clears the pending operation without applying any inputs. After an effect, return a failure and its completed effects instead of continuing with a correction. Archive and Promote Draft forward an ordered batch to the same backend operations. Return the backend outcome under CA-R-1105 without replay or repair. The backend reuses the current Workbench Scope Unit projection, so a newly indexed valid Scope Unit is available without a runtime restart.

#### Initiative-bound procedure

Apply this procedure to Initiative-bound project-local Atom Tools.

1. Preserve the human-origin Initiative **and** select the one canonical Atom Tool **without** resolving its target **or** lifecycle meaning.
2. Forward the sealed request **to** that Tool **and** return its structured outcome unchanged.
3. Report success **only** **after** the canonical Tool returns its acknowledged outcome; preserve a rejection, conflict, partial result, **or** blocked result as such.

#### Outcome

The backend owns target selection, effects and verification. MCP forwards the request and reports the outcome.

#### Initiative-bound failure or stop

Stop and return an explicit failure if the Initiative, authorization, canonical Tool selection or Tool outcome is absent or invalid.
