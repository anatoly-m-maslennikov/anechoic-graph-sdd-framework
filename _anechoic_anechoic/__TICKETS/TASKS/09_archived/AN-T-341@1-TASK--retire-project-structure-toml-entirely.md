---
atom_family: TKT
atom_id: AN-T-341
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 18:26:00 +0400
---
## Summary

Retire project_structure.toml entirely

## Objective

Retire obsolete governing Atoms and remove the live TOML file. Replace every production reader with Declaration-Atom sources; retire TOML row editors and file-only bindings. Update affected fixtures and documentation. Do not preserve a fallback or derived compatibility TOML.
