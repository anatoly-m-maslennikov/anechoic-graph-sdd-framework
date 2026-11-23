---
atom_family: TKT
atom_id: AN-T-2791
container:
  component: C00
priority: 2
context:
  template: epic
state:
  status: archived
  version: 1
  updated_at: '2026-11-17T17:30:53.917255+00:00'
---
## Summary

Apply the Anechoic model to the project

## Objective

Migrate Project records and their full history mechanically to the approved
Anechoic model. Verify the migrated data and runtime while Local Release
continues to build from the protected legacy inputs.

## Work

1. **Verify the model inputs.** Check the CA-P-3089 packet's `SHA256SUMS`
   and rerun its model and carrier checks. Use the shared generator and
   validator from CA-P-3048. Check the latest carrier paths in CA-R-3168
   and CA-A-1466 and the upstream-only import rule in CA-R-3169.
   CA-C-745 remains open in the tracker. Use CA-R-3169 for layer validation.

2. **Protect the legacy build.** Capture the actual Local Release inputs
   by path and content digest, with Atom IDs and versions where applicable.
   Include settings, Scope Unit sources, and selected Workflow, Step,
   Action, and callback pins. Preserve the selected files at their original
   paths throughout migration. Check source staging and package selection
   with both record trees present so the legacy release keeps its agreed
   inputs and excludes the new raw record tree. This can run alongside 1.

3. **Freeze the shared migration map.** Depends on 1. Inventory every
   in-scope carrier, including Methodology, and its original path, physical
   modification time, status, version, and body digest. Include authored
   relations, containers, and version-pinned consumers such as trace
   sidecars. Assign IDs in three Project-wide sequences, AN-S, AN-T, and
   AN-P. In each sequence process Archived, Current, and Draft in that
   order, oldest physical modification time first, with original path
   breaking ties. Reuse a numbered Atom's new ID for all its revisions.
   Distinguish unnumbered Drafts by original path. Verify that repeating
   allocation yields the same map regardless of batch order.

4. **Rehearse the mechanical conversion.** Depends on 2 and 3. Stage
   the converted records before applying them. Use R → DES, M → SWD,
   E → QA, and D → DevOps. Convert archived Implementation records to
   TKT Issue / Code-Spec Mismatch. Linked Steps and Actions follow their
   Workflow family. Unlinked Steps and Actions use PMETA and stay unlinked.
   Use the first stored main subject, drop `topics.dependencies`, and
   record the original subject and source reference when the Concern
   cannot be mapped. Apply only the approved structural and status maps.
   Check duplicate identities, exact revision pins, and destination
   collisions, including case-only conflicts. Report ambiguous carriers,
   unassigned Ticket branches, or Active SPEC without an admitted lens.
   CA-C-746 holds PMETA status paths and TKT Backlog placement. Reserve
   their IDs in the shared map and retain their sources until placement
   is decided. Continue rehearsing independently placeable batches.

5. **Apply verified batches.** Depends on 4 for each batch. CA-P-3075
   applies the Project batches outside Methodology. CA-P-3078 applies its
   frozen slice once to Meta-ontology with the migration lens whitelist
   and supplies its batch verification. Remap stable and exact references,
   preserve every pinned version and Draft qualifier, and regenerate Views
   and direct inverse relations. Keep archived Implementation records in
   `__TKT/ISSUES/archived/`. Verify Active SPEC lens paths and the separate
   TASKS and ISSUES status directories. Preserve body text and revision
   history through the mechanical pass.

6. **Verify legacy Local Release continuity.** Depends on 5. Compare the
   actual selected input paths and digests against 2 and perform a clean
   legacy rebuild on an isolated checkout containing both trees. Record
   the selected inputs, rebuilt image, and package selection evidence.

7. **Verify the migrated Project.** Depends on 5, including the mechanical
   Methodology batch in CA-P-3078. Check that every source revision and
   reference is accounted for in the migrated Project. Verify all four
   trees, exact legacy and new revision lookup, cross-batch relations,
   regenerated Views, and the migrated index through MCP. Run lifecycle
   and admitted Workflow checks against an isolated copy of the real
   migrated Project. Finish the Epic after 6 and 7 pass and every held
   record has an approved destination or disposition.

## Boundaries

CA-P-3073 owns Project and Component renames. Coordinate shared names and
paths before migration. Keep protected legacy inputs in place while the
build depends on them. CA-P-3076 owns content cleanup after the mechanical
baseline. CA-P-3077 owns Workbench improvements. The later editorial split
to Meta-methodology stays in CA-P-3078.

## References

CA-P-3074, CA-P-3089, CA-A-1461 through CA-A-1466, CA-R-3168 through
CA-R-3203, CA-C-745, and CA-C-746.
