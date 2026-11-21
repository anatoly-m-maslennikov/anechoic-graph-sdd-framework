---
atom_family: TKT
atom_id: AN-T-2757
container:
  component: C9
priority: 2
context:
  template: task
  label: Epic
state:
  status: done
  version: 1
  updated_at: '2026-11-17T17:30:50.879370+00:00'
---
## Summary

Create the Anechoic model

## Objective

Produce an approved, validated model for Anechoic before migrating existing records.

## Work

Tasks 1 and 2 can start in parallel. Each modeling task produces governing
Draft Atoms and its acceptance examples. Use the reviewed proposals as inputs.

1. **Define Project layout and Component Manifests**. Use CA-A-1461 and
   CA-A-1463. Verify REAL, SPEC, PMETA, and TKT roots, including exclusion
   of `_PMETA/` and `_TKT/` from SPEC. Define Purpose, Manifest, Contract
   and their tiers. Verify the Project Component and its three direct children.
2. **Define the graph and Atom identity**. Use CA-A-1462. Define the
   primary entities, S/T/P IDs, revision references, Component parentage,
   Atom containers, and named classifications. Verify direct inverses
   and put transitive results in Views.
3. **Define Concern paths and lens validation**. Blocked by task 2. Verify
   the three Concern fields, full paths, and both hops in
   `Model/Graph/Node//Artifact`. Cover absent, inherited, and explicit
   empty lens whitelists. Accept SPEC with DES and SWE. Accept SWE with
   SWD and QA when DevOps is omitted. Reject sibling DES and SYS because
   both cover DOM.
4. **Define Spec templates and their effects**. Blocked by tasks 1–3.
   Define allowable axes, claim formats, and tiers. Verify Decision and
   Standard effects, Solution contributions and cycle rejection, and
   top-down Policy selection across Component boundaries.
5. **Define Package Specs and trace bindings**. Blocked by tasks 1 and 2.
   Verify a single PKG Spec with a stable ID, short Purpose, and Contract
   for an ordinary Package. Check placement directly under its Component
   Package. Verify that sidecars bind existing Realization to Spec Atoms
   and that Realization paths resolve from the Project root.
6. **Define package exports and import checks**. Blocked by task 5. Test
   Internal defaults for all Package categories, Public and Internal
   allowlists, and caller rules inherited by nested ordinary Packages and
   child Components. Test `__<visibility>.<extension>` with normal Python
   imports. Check a behavior Contract with no export list and explicit
   nonempty and empty lists. Accept direct import of a named Unit and
   reject importing its whole Module when only the Unit is exported.
7. **Define and check I/O allowances**. Blocked by task 4. Finalize the
   channel definitions and validation approach. Test the `all` default,
   directional inheritance, explicit child allowances, and a Policy that
   reports the reason for a violation on a child Manifest. Check imports
   of I/O libraries for wholly forbidden channels. API input admits GET,
   HEAD, and OPTIONS. API output covers POST, PUT, PATCH, and DELETE.
8. **Define authoring, Tickets, and Workflow Runs**. Blocked by task 2.
   Use CA-A-1464. Verify same-ID Draft edits and promotion for Current
   SPEC, PMETA, and Tasks, in-place edits for Draft and Current TKT assets,
   and status transitions that preserve ID and Version. Verify separate
   Work Log and asset IDs and direct Task links under one Epic. Specify
   that only PMETA Workflows govern Ticket Atoms. Test an Active-only
   Workflow launch and exact revision pins. CA-C-744 tracks the deferred
   shared reference from Runs to Tasks.
9. **Generate and validate the review model**. Blocked by tasks 3–8.
   Coordinate with the programmatic foundation in CA-P-3048. Finalize
   Header fields and the filename formula. Build the machine-readable
   definitions and run the representative positive and negative cases,
   including one local PMETA extension and migration carrier examples.
10. **Approve the model and hand it off**. Blocked by task 9. Review and
    fix the governing Drafts, confirm the model with the Operator, and
    deliver the approved Atoms, generated definitions, and verification
    results to CA-P-3075.

CA-P-3075 owns the frozen inventory and ID map, mechanical migration, and
verification of retained Local Release inputs. CA-P-3078 consumes the same
map for its Methodology migration and later cleanup.

## References

CA-A-1461 through CA-A-1465. Coordinate with CA-P-3048, which tracks the Programmatic Model foundation.
