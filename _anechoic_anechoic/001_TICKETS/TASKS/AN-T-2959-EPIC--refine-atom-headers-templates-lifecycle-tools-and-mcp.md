---
atom_family: TKT
atom_id: AN-T-2959
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-21T18:46:48.656974+00:00'
---
## Summary

Refine Atom Headers, Templates, Lifecycle Tools, and MCP

## Outcome

The authored Header defines each Atom. The compiled Model validates its Header and Template. Lifecycle tools and MCP use the same checks and derive file names and placement from the authored Atom.

## Delivery order

1. Finalize the common Header structure, field order, and Template rules
   for SPEC and TKT. Preserve the Task Template and its navigation labels.
2. Migrate the SPEC and TKT carriers to the agreed Header. Verify IDs,
   exact revision references, authored content, and derived placement.
3. Revise the backend lifecycle methods and MCP tools. Enforce the new
   SPEC Templates, create attached and detached Ticket Assets, and archive
   SPEC Drafts. Verify the packaged runtime and Workbench.

## References

AN-S-3160, AN-S-3176, AN-S-3193, AN-S-3196, AN-S-3199, AN-T-2932.
