---
atom_family: SPEC
atom_id: AN-S-1734
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 25
  updated_at: '2026-11-25T21:55:25.706455+00:00'
---
## Summary

Validate lifecycle Workflow adaptability

## Claim

### Prose Claim


a status-change Workflow **and** its target Entity's applicable model.


the Evaluation **must** check that a status-change Workflow follows the target Entity's applicable model under AN-S-1616.

## Details

- supply **`=2`** applicable status models with different admitted values, including a newly admitted value absent from the original model; the same Workflow definition **must** support their admitted values. For legacy Content Role/Type Atom creation and explicit Status updates, check selection under that profile. For native Atoms, check the applicable Family values and the transitions in AN-S-1604. Reject disallowed transitions.
- Resolve the native model by Atom Family and the legacy model by qualified Content Role and Type.
- supply an applicable Scope Unit **or** Atom Collection model; admit its valid change **without** imposing an Atom lifecycle.
- request an unknown value or a change **without** a defined model: reject **without** inventing a value **or** bypassing required Carrier behavior. For a non-Atom Entity model that defines transition conditions, reject its prohibited transition; do not apply that matrix as an Atom Status gate. Preserve ordinary schema, identity/collision, expected-source/currentness, permission and Carrier safeguards.
- supply a model requiring an unsupported capability: require an explicit limitation rather than a false pass.

these cases validate the methodology definition; an executor requires separate Implementation checks.
