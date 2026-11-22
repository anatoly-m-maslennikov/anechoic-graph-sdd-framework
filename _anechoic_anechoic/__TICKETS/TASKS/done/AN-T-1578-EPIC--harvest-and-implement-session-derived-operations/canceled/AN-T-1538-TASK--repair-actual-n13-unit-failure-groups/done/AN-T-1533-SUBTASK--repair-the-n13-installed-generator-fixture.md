---
atom_family: TKT
atom_id: AN-T-1533
container:
  atom: AN-T-1538
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Repair the N13 installed generator fixture

## Objective

repair the graph fixture against the current verified installation schema while preserving canonical output independence from the executed generator Carrier.

## Details

test_generate_project_graph_state.py; no product graph-semantic change is authorized by this fixture mismatch.

## Definition of Done

the confirmed defect is explained and repaired against current authority; source-equivalent focused regressions have a captured terminal result and independent review accepts the bounded change. actual full Release acceptance remains with the parent Plan.

## Acceptance evidence

independent acceptance passed the full graph fixture module: 14 tests, 25.947 seconds, exit 0, using host-tests Python. the fixture builds a schema-valid verified installed package and preserves canonical output independence from the actual executed Carrier.

this is bounded fixture acceptance only; the complete fresh Release gate remains with CA-P-1809 and CA-P-1117.
