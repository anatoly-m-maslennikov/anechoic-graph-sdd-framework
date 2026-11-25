---
atom_family: SPEC
atom_id: AN-S-4797
container:
  component: C67
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3332
state:
  status: draft
  version: 2
  updated_at: '2026-11-24T17:28:40+00:00'
---

## Summary

Serve an admitted Beta Project generation

## Guarantee

Keep the Database Server and Model and Structure Hosts within the Kernel process. Bind the server to one Project instance. Admit and serve the generation built by C69 through CS4 and CS1. If Kernel admission fails, retain the prior generation.

For an invalid Model candidate, CS1 selects the last accepted Model or, if none exists, the reviewed bundle. Report the candidate diagnostics.

Serve the accepted Model and generation ID to requests for that instance. Reconstruct canonical Structure JSON from the accepted `mrt_project_structure` rows and the accepted generation facts. Return it with that generation ID. Publish changed rows atomically through ingestion.

Reject requests for another instance. Report candidate admission failures and diagnostics. Before an accepted generation is available, report that state.
