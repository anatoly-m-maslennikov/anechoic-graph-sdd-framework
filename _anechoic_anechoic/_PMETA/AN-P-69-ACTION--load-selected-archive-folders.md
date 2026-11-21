---
atom_family: PMETA
atom_id: AN-P-69
structure:
  container:
    component: C45
context:
  template: action
state:
  status: active
  version: 1
  updated_at: '2026-11-12T01:39:58.202981+00:00'
---
## Summary

Load selected Archive folders

## Operation

### Claim scope

One explicit Workbench request to load the Archive folders for selected Scope Units and Roles.

### Claim

Resolve each requested Scope Unit and Role to its model-declared Archive folder and admitted aliases. Validate the selection before reading or publishing any Archive rows. Load the selected physical files into the existing `atoms` table, and return the complete set of Archive scopes loaded by this Workbench owner. A load of the same unchanged folders creates no duplicate rows. Queue audits of the loaded files and make their progress observable through Workbench status. Return explicit selection or source errors. This Action leaves the source files untouched.