---
atom_family: SPEC
atom_id: AN-S-1734
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Validate lifecycle Workflow adaptability

# Summary

Validate lifecycle Workflow adaptability

## Scope

a status-change Workflow **and** its target Entity's applicable model.

## Claim

the Evaluation **must** check that a status-change Workflow follows the target Entity's applicable model under CA-R-1521.

## Details

- supply **`=2`** applicable status models with different admitted values, including a newly admitted value absent from the original model; the same Workflow definition **must** support their admitted values. For Atom creation and explicit Atom Status updates, verify every value admitted by the qualified Content Role/Type model is selectable without a required intermediate Status or transition matrix.
- specialize an Atom's model by Content Role **and** Type; checking **only** a universal Atom value list fails.
- supply an applicable Scope Unit **or** Atom Collection model; admit its valid change **without** imposing an Atom lifecycle.
- request an unknown value or a change **without** a defined model: reject **without** inventing a value **or** bypassing required Carrier behavior. For a non-Atom Entity model that defines transition conditions, reject its prohibited transition; do not apply that matrix as an Atom Status gate. Preserve ordinary schema, identity/collision, expected-source/currentness, permission and Carrier safeguards.
- supply a model requiring an unsupported capability: require an explicit limitation rather than a false pass.

these cases validate the methodology definition; an executor requires separate Implementation checks.
