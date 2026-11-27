---
atom_family: SPEC
atom_id: AN-S-3399
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-23T09:32:30.312767+00:00'
---

## Summary

Detect workflow regions that can reuse an existing Action

## Claim

### Prose Claim

Use Realization Graph Code Units, call edges, and source-derived
transitions to find a region with one entry that could call an existing
Action. Propose an explicit argument mapping. Keep the surrounding
workflow, including its setup and completion.

In Lean, compare the selected region with the proposed call over the
admitted inputs and starting states. Check the callee's preconditions,
results, errors, and effects. Preserve effect targets, order, and
multiplicity. Check the declared import and state boundaries before
reporting reuse as available.

Report the source range, callee, arguments, and evidence. Record a
counterexample when behaviors differ. Mark incomplete path or effect
coverage unresolved. Produce findings for review.

## Details

Select caller and callee Code Units in one Python Module. Check the
first consecutive dictionary writes and following result, or supply
the exact caller range. Use exact built-in dictionaries with string
keys and immutable scalar values. Assume stable bindings and state at
region entry and during the modeled code.

Run `python -m IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_reuse` with JSON on stdin. Supply the Project root,
control root, exported Beta graph, compiled Structure, and both Code
Unit keys. Supply `first` and `last` together to select the region.
The finding includes the source digest, proposed arguments, and the
Lean verdict.

Verify one parameterized Python pair, an extra-write counterexample,
and unresolved coverage for unsupported source.
