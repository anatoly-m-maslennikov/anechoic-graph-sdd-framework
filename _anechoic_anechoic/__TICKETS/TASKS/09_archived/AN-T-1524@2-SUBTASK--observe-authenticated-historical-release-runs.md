---
atom_family: TKT
atom_id: AN-T-1524
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:34 +0400
---
## Summary

Observe authenticated historical Release Runs

# Summary

Observe authenticated historical Release Runs

## Objective

repair the read-only Release-host observer so a current-source change does not prevent reading exact authenticated saved Run evidence.

## Details

- preserve the frozen request identity, exact Release route, retained transport binding, namespace and worker availability checks before database access.
- keep current-source guards on dispatch and actual recovery; an observation is not a new admission, grant, replay or status rewrite.
- use bounded regression fixtures and independently review the separation before root checks the actual historical N12 status through MCP.

## Definition of Done

focused tests prove truthful historical observation after source drift, pre-client refusal of foreign or tampered bindings and unchanged strict dispatch/recovery guards; independent review accepts the change and the live N12 observer returns its actual recorded state.

## Result

the 15-case Release-host backend suite passes, and independent review accepts the private observation/effect split. status and recovery-status preserve exact frozen identity, retained transport/availability checks and pre-client tamper/foreign refusals; actual dispatch and recovery retain strict current-source validation. after the explicit restart of the identified idle Release-host worker, live MCP reads historical N12 with its eight completed and three interrupted terminal Runs and 22 durable receipts. scheduler SUCCESS remains distinct from the actual interrupted-pending work outcome; no replay, effect or release success is inferred.
