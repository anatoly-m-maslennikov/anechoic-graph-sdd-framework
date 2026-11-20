---
identity:
  atom_id: AN-T-2791
context:
  container:
    component: C00
  tier: 3
  template: epic
state:
  status: "done"
  version: 8
  updated_at: "2026-11-20T12:33:35.721050+00:00"
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
   and CA-A-1466, including the PMETA and Backlog placements decided in
   CA-C-746, and the upstream-only import rule in CA-R-3169.
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
   Distinguish unnumbered Drafts by original path. Give each approved
   unnumbered Archive its own ID, preserving its Version and path alias.
   Apply the same rule to every withdrawn Draft whose old ID and Version
   collide with an ordinary revision. Give the withdrawn carrier a separate
   Archived ID, keep its Version and old `-draft` pin, and preserve the
   ordinary lineage. Verify allocation is independent of batch order.

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
   Verify Active PMETA at its root with shared Draft and Archived paths,
   and keep Backlog in its Ticket branch. Copy legacy archive titles into
   Summary while retaining the original Markdown below it. Route records
   from retired Community Extensions, Core Extensions, and Field to the
   Project, preserving their history. Keep Framework Delivery and Operator
   Documentation as direct Project children. Migrate otherwise valid carriers
   with their verified relations. Keep each unresolved relation in the
   migration receipt with its original name, target, and source evidence.
   Reserve IDs for any held carriers whose identities and families are known.
   Continue rehearsing placeable batches.

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
   migrated Project. The mechanical migration is complete after 6 and 7
   pass and every held record has an approved destination or disposition.

### Component boundaries

Start after the Component rename in CA-P-3073.

- Specify, implement, and verify Code Access in the Model and Engine per
  CA-A-1463. Ship a standalone report with separate results for denied and
  unresolved imports. Local Release keeps its existing gates.
- Shared State and runtime I/O design and enforcement moved to AN-T-2921.

### Manifest Runtime

- AN-T-2916 specifies the Component and its three Packages.
- AN-T-2917 implements Manifest Compiler, AN-T-2918 implements Model Host,
  and AN-T-2919 implements Structure Host. These can run in parallel
  once the Package interfaces are specified.
- AN-T-2920 integrates all three and verifies the packaged runtime.

## Boundaries

CA-P-3073 owns Project and Component renames. Coordinate shared names and
paths before migration. Keep protected legacy inputs in place while the
build depends on them. CA-P-3076 owns content cleanup after the mechanical
baseline. CA-P-3077 owns Workbench improvements. The later editorial split
to Meta-methodology stays in CA-P-3078.

## References

CA-P-3074, CA-P-3089, CA-A-1461 through CA-A-1466, CA-R-3168 through
CA-R-3203, CA-C-745, CA-C-746, CA-C-749, and CA-C-750.
