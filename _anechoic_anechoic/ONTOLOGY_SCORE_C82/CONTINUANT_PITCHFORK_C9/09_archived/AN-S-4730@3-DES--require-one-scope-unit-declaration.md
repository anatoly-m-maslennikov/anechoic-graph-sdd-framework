---
atom_family: SPEC
atom_id: AN-S-4730
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-05 12:58:42 +0400
---
## Summary

Require one Scope Unit Declaration

## Claim

### Prose Claim


Each Scope Unit, including Project.


Every specific Scope Unit, including Project, except the predefined Scope Unit `world`, has exactly one external Requirement Atom with Form `Scope Unit Declaration` and an active Subject naming that Scope Unit. The Declaration is the sole structural authority for its declared values. `world` has ID `CA-SU--1` and has no Scope Unit Declaration.

The Declaration carries the Scope Unit Name, stable ID, ordered state, optional Label, conditional order.number and direct containment. Project has a stable ID, is unordered and has no order.number. Each non-root Scope Unit other than `world` has one direct Parent; Project has none.

Authority and Delivery folder names are derived from the Declaration. `project_structure.toml` is not a governing source.

## Details

The Project Declaration is externally Operator-owned. The Operator is an Actor, not a Scope Unit.
