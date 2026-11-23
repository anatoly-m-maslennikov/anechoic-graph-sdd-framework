---
atom_family: SPEC
atom_id: AN-S-1172
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 17:04:05 +0400
---
## Summary

Validate project integrity

# Validate project integrity

the framework **must** provide one deterministic read-only Tool that validates a selected Project scope as one integrated repository.

the Tool **must** apply Carrier validation **to** **every** selected Atom **and** check **all** of the following:

- unique identity resolution;
- registered structural **and** lifecycle topology;
- registered Relation **and** authority-graph rules applicable **to** RMEDO Atoms;
- authority modes **and** applicable Settings authority;
- Projection currentness;
- Journal replay integrity;
- Revision **and** proof provenance;
- generated-data stage direction;
- control-root/runtime hygiene.

the Tool **must** emit stable diagnostics **without** mutating Project files.
