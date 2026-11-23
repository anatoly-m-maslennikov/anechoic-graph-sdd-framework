---
atom_family: TKT
atom_id: AN-T-7
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 2
  updated_at: 2026-08-30 19:44:59 +0400
---
## Summary

Repair Lowercase anechoic Project Identity Authority

# Repair Lowercase anechoic Project Identity Authority

**when** CA-P-928 is Done, **then** the Assignee **must** make `anechoic` the canonical Project key and name while preserving `ANECHOIC` as the Framework name and `CA` as the Project Atom ID prefix.

## Scope

`((the active Project canonical-name authority) union (the canonical Local Configuration Project Configuration Carrier fields that identify the Project) union (their exact revision archives and completion evidence))`

## Definition of Done

the Task is **not done if** (**any** active authority identifies the Project as uppercase `ANECHOIC` **or** **any** changed Project Configuration field identifies the Project as uppercase `ANECHOIC` **or** the repair changes the Framework name **or** the Project Atom ID prefix **or** an immutable admitted Atom ID **or** a changed Atom lacks its exact predecessor archive).

## Details

apply the Operator distinction exactly: `ANECHOIC` names the Framework, `anechoic` names the Project, **and** `CA` remains the Project Atom ID prefix.

## Completion Evidence

the Task repaired the two explicit active Project identity authorities, set the native Project Configuration key and name to `anechoic`, and appended the version `4` identity-and-digest binding for `ANECHOIC-I-001`. the non-authoritative execution evidence is stored in `execution_evidence/CA-P-929@2-lowercase-anechoic-project-identity-authority-repair.projection.json`.
