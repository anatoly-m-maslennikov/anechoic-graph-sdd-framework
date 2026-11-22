---
atom_family: TKT
atom_id: AN-T-2684
container:
  atom: AN-T-2737
priority: 2
context:
  template: task
  label: Subtask
state:
  status: canceled
  version: 6
  updated_at: '2026-11-20T20:06:18.682056+00:00'
---
# Summary

Compile and validate the detached current Workflow candidate

## Objective

After CA-P-2620 completes and both semantic Problems are resolved or explicitly
accepted, compile a detached O016 candidate and validate its graph, route,
registry and contract drift without changing the visible Project binding.

## Details

This is one bounded review Task with at most 15 minutes of own work. Use only
the requalified current source pins and preserved frozen oracle. Validate graph
structure, terminal distinctions, route/admission membership, A1142/W09
handling and exact source hashes. Do not broaden the candidate frontier,
silently add move_atom, rewrite source, emit or admit a live candidate,
mutate a manifest/projection, run production MCP, replay calls, implement
Scope Units, release or deploy.

## Definition of Done

Produce a detached candidate and compact validation report with explicit
accepted, rejected and unresolved drift. Candidate validity must remain
separate from publication, runtime admission, live binding, release and
deployment decisions.

### C584 candidate-direction checkpoint — 23 October 2026

The detached candidate's operation set must omit optional move_atom; the
optional implementation capability remains preserved for a later compatible
frontier decision. O127's internal Move does not admit a public MCP route.
The live Project manifest still has 16 operations and remains untouched.
Compilation and validation stay conditional on CA-C-584's validated
correction; no runtime, public-contract or publication completion is claimed.
