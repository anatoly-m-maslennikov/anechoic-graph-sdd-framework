---
atom_id: CA-R-1430
ref_id: CA-R-1430
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Project.Settings.Authority Modes
  dependencies:
  - ANECHOIC_MODEL <+ Project.Settings
  - ANECHOIC_MODEL <+ Scope Unit/Project
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Atom
tier: 2
status: Active
version: 27
updated_at: 2026-11-02 20:07:03 +0400
---
## Summary

Select Authority Modes through Framework Instance Settings

## Claim

Framework Instance Settings select the Project Authority Mode and Default Scope Unit Authority Mode. Permitted values are `strict` and `casual`. Neither changes the authority of active Atoms.
