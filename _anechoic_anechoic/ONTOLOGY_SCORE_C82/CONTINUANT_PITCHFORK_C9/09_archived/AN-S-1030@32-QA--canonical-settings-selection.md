---
atom_family: SPEC
atom_id: AN-S-1030
container:
  component: C9
tier: 7
context:
  lens: QA
state:
  status: archived
  version: 32
  updated_at: 2026-10-25 05:14:10 +0400
---
## Summary

Canonical Settings Selection

# Summary
Canonical Settings Selection

## Scope
Framework Instance Settings, Project Settings, **and** Project Structure selections.

## Claim
### Claim checked

the Framework Instance Settings Artifact **and** Project Settings Artifact accept exactly their registered values, resolve deterministically, **and** fail closed on invalid **or** unknown selections; Project Structure owns current unit declarations **and** explicit per-unit overrides **without** duplicating Settings selections **or** requiring a structural Projection.

### Applicable conditions

1. resolve **and** load the exact current anechoic_framework_settings Artifact **and** anechoic_<project_name>_settings Artifact **and** the Default Settings Artifact; evaluate framework parameter resolution against `CA-E-450-CORE_META_MODEL-POLICY--validate-framework-parameter-fallback`.
2. accept **only** enabled catalog Artifact Types, Atom Content Roles **and** their qualified Types, **and** Governance Origins.
3. accept **only** `medium` **or** `high` artifact creation strictness.
4. accept **only** `silent` **or** `verbose` interaction reporting. select **every** allowed value through Framework Instance Settings **and** confirm that the effective reporting default follows that selection **without** changing source Atoms, using Project Settings as reporting authority, **or** applying an independent Atom-fixed default.
5. validate initialization inputs against Project Settings field authority **and** default **and** Project Authority Modes against Framework Instance Settings field authority, **and** explicit per-unit overrides against Project Structure field authority; do **not** hard-code this Project's selected values **in** the Evaluation.
6. reject unknown keys **when** the governing schema marks their table closed.
7. confirm a second parse produces identical effective settings **and** direct Project Structure resolution uses the same selected declaration bytes **and** consumed Settings revisions, including Default Settings **when** it supplies consumed values; deleting a legacy structural Projection does **not** change those results.

### Acceptance criteria

**every** valid selection resolves deterministically **and** **every** invalid selection fails closed with the exact key **and** allowed values.

### Failure disposition

record a Concern naming the accepted invalid value, rejected valid value, **or** non-deterministic result **and** stop settings-schema readiness.

## Details
