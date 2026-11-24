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
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---
## Summary

Serve an admitted Beta Project generation

## Guarantee

Keep the Database Server and the Model and Structure Hosts within the
Kernel process. Bind the server to one Project instance. Admit the paired
artifacts and Project snapshot as one generation; retain the prior generation
if admission fails.

For a request bound to that instance, serve the accepted Model or Structure
bytes with their generation ID. Before admission, report that no generation
is available. Reject a request for another instance.

## References

AN-S-3332, AN-S-3335, AN-S-3343, and AN-S-3344.
