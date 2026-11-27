---
atom_family: TKT
atom_id: AN-T-4046
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: done
  version: 1
  updated_at: "2026-11-27T01:12:04.381165+00:00"
---
## Summary

Make the Formal Model the source of Model rules

## Objective

Finalize Formal Model (C51) in Spec Engine (C75). Declare Model
rules once in Formal Manifests, compile them, and verify the result
with Project Structure (C93) and Formal Specification (C94).

## Scope

Cover entities, properties, allowed and fixed values, defaults,
relation endpoints and inverses, templates, and Model-governed
statuses. Review for conflicts, gaps, and ambiguous declarations.

Align the Model Component Manifests and Solutions with the compiler,
bundled Model, and validation. Verify the interfaces with both
siblings through C75. Update Atom lifecycle, ingestion, and Kernel
validation where they consume the Project Config rules below.

## Project Config

Compile permitted Project Config extensions to templates, statuses,
allowed values, and defaults.

### Project Config changes by effort

| Effort | Change | Work required |
| --- | --- | --- |
| Smallest | Add a Project Spec template | Use the compiled Model to select and validate the template during creation and promotion. |
| Small | Disable a template for new creation | Check eligibility in lifecycle and keep the definition available for existing Atoms and history. |
| Medium | Add a status within Current | Define how Project Config extends the status list and align ingestion, transitions, and Kernel validation. |

## Done when

- The Model tree and primary-entity projection match the Active Formal
  Manifests, including fixed values and Relation counterparts.
- C75 compiles a disposable Project, verifies its Structure against the
  compiled Model, and verifies a Component Manifest and Solution through
  Formal Specification.
- Valid Project Config extensions compile without compiler changes.
  Invalid declarations report diagnostics and leave the accepted Model
  intact. Verify the bundled Model and reuse with matching inputs.
- On a disposable Project, create and promote a Spec with an added
  template. Disable creation with that template and verify that existing
  Atoms and their history remain readable.
- Add a Project Config status to Current and verify that ingestion,
  lifecycle transitions, and Kernel validation apply the same rule.
