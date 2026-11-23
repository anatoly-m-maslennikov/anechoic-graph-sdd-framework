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
  status: "in_queue"
  version: 3
  updated_at: "2026-11-23T04:15:56.530718+00:00"
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

4. Replace full projection rebuilds after lifecycle writes with incremental
   refresh. Verify each transition and report its outcome and duration.
5. Read lifecycle facts from the admitted Kernel generation through SQL.
   Let Adapters read only carriers addressed by the operation. Allocate
   new Atom IDs through the serialized lifecycle lane.
6. Bring the slowest supported single-Atom operation below 0.5 seconds.
   Reuse loaded lifecycle code. Apply only the addressed carrier delta.

## Lifecycle transition coverage

Use the active Model and registered lifecycle routes to enumerate every
allowed source-to-target transition for SPEC, TKT, and PROJECT_CONFIG.
Extend the host matrix from AN-T-2966 and the packaged MCP tests from
AN-T-2963. Cover creation, revision, publication, status change and
archive wherever declared. Mark declared transitions with no route as
coverage gaps. Test that refused transitions leave source and index unchanged.

Apply the carrier changes from each accepted transition to the affected
projection rows and relations, including removals and archived revisions.
Check the generation trace for each case to verify MCP sees the change
without a full projection rebuild.

Record family, Template, operation, source and target Status, expected and
actual outcome, pass or fail, and elapsed seconds for each case. Measure
from request submission until the expected result is visible through MCP.
Verify the exact revision and indexed Status for accepted transitions.
Report setup separately and attach the source revision and candidate image
ID. Use elapsed time to compare cases and expose regressions.

Measure each supported single-Atom operation from the MCP request to
successful SQL readback on a ready runtime. Report the maximum across
the operations. Record timing for operations that change multiple Atoms separately.

## References

AN-S-3160, AN-S-3176, AN-C-3193, AN-S-3196, AN-S-3199, AN-T-2932.
