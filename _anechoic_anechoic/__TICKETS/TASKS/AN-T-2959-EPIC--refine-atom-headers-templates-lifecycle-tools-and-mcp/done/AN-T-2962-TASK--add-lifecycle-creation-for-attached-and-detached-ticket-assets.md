---
atom_family: TKT
atom_id: AN-T-2962
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-21T20:44:08.058651+00:00"
---
## Summary

Add lifecycle creation for attached and detached Ticket Assets

## Work

After Header migration, provide one backend creation operation for Spec
Proposal, Analysis Report, Work Report, and Work Log. Accept an optional
owning Task or Epic. Derive attached placement in the owner's companion
ASSETS directory and detached placement in the Project's __TKT/ASSETS
directory.

Verify both placements, rejection of invalid owners and templates, and visibility of the saved carrier in Workbench.
