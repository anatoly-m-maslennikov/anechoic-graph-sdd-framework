---
identity:
  atom_id: CA-P-3073
  ref_id: CA-P-3073
context:
  container:
    scope_unit: CA-SU-00
  role: plan
  form: plan
  label: Epic
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC
  tier: 3
state:
  status: active
  version: 1
  updated_at: '2026-11-17T17:30:46.834267+00:00'
destination:
  file:
    name: CA-P-3073-EPIC--rename-the-project-and-framework-components-to-anechoic.md
    path: .anechoic_anechoic/03_plan
---
## Summary

Rename the project and framework components to Anechoic

## Objective

Rename the Components and move their code folders. Prepare the cutover,
lens folders, and technical cleanup.

## Work

The repository rename is complete. Local release `0.4.4.47` verified the new name.

CA-P-3075 owns carrier migration and legacy release proof. CA-P-3078 owns
Methodology moves. CA-P-3076 owns Specification content cleanup.

## Tasks

Start the inventories and path checks in parallel.
Agree on the shared names and paths with CA-P-3075 before migration. Assign one
owner to any shared moves, configuration files, or path references. Make
edits in parallel where the paths and files are separate.

### Component rename and Engine Studio split

- [x] Record C14’s descendant IDs, parents, and paths before any split.
  The baseline records C14 and 37 descendants in
  `.anechoic_tmp/ca-p-3073/c14-before-split.json`.
- [x] Check the five direct Project children against CA-A-1461, “Framework
  Components”, and the confirmed placements in CA-C-749.
- [ ] Apply the confirmed layer order. Meta-ontology is Layer 1,
  Meta-methodology is Layer 2, and Engine Studio is Layer 3.
- [ ] Apply the Component names and placements. Move C14 as a unit and retain
  its descendant IDs and parent links in the mechanical migration baseline.
  The isolated replay verified the Project Manifest, 42 Component Manifests,
  and their direct and inverse containment edges. It preserved all 37 C14
  descendant IDs and mechanical parents. See
  `.anechoic_tmp/ca-p-3073/c14-structural-replay/receipt.json`. All 76 legacy
  structural source digests have Git and rename evidence in
  `.anechoic_tmp/ca-p-3073/structural-source-provenance.json`.
- [ ] After the C14 move and baseline check, apply the Engine Studio split in
  CA-A-1461. Place the four Components directly under Engine Studio.
  Reuse C21 for MCP Patchbay and C43 for IWE Console. Keep the current
  Workbench backend under C43. Assign new IDs to Kernel Mixer and Backend
  Deck. Defer the lifecycle code moves. Later, move the run coordinator and
  its synchronous write backend into Kernel Mixer. See the topology plan and
  candidate IDs in `.anechoic_tmp/ca-p-3073/component-topology-plan.json`.
- [ ] Verify the renamed paths, references, and existing build. Hand off the
  confirmed Component paths to CA-P-3075 for its Component boundary work.
  The mechanical path corrections for C14 and its 37 descendants are in
  `.anechoic_tmp/ca-p-3073/component-path-handoff.json`. They preserve the
  mechanical parent links and give both staging and final SPEC paths.

### Engine Studio code folders

- [x] Inventory tracked code and configuration that refers to
  `LAYER_2_FRAMEWORK_ENGINE/`. Distinguish current callers and generated
  inputs from historical record paths.
- [x] Move the C14 code tree as a unit from `LAYER_2_FRAMEWORK_ENGINE/`
  to `LAYER_3_ENGINE_STUDIO_C14/` in commit `3a63478fec`.
- [x] Update active release, package, Docker, and launcher paths for the new
  root.
- [x] Update active imports, tests, tooling configuration, and documentation
  for the new root. Refresh affected generated or path-pinned assets from
  their sources. Package preparation passed with both existing and refreshed
  assets. The generated assets matched the committed files.
- [x] Check that the existing build works from the new root before the split.
  The isolated checkout matched the tracked tree of `3a63478fec`. The Docker
  build with existing assets passed. Refreshing the assets resolved to the
  same immutable image. Both Docker Workbench MCP and HTTP tests passed.
  Build and test logs are under `.anechoic_tmp/ca-p-3073/`.
- [x] Move the IWE Console and MCP Patchbay code into their Component
  folders. Commit `53d820ce6b` moved both code trees and kept the
  Workbench backend with IWE Console. The current caller checks passed
  100 focused tests. The isolated C21/C43 rehearsal is commit `ce1030270d`.
  Its image build and both Docker Workbench MCP and HTTP tests passed. The
  combined rehearsal with native runtime is `52465f61ba`. Its image built,
  and its normal Docker launcher passed native MCP alias and Workbench View
  checks. The replay patch against `189f757401` is
  `.anechoic_tmp/ca-p-3073/component-split-after-native.patch`.

### Atom IDs and references

- [x] Prepare a compact old-ID and new-ID file for the isolated Active
  preview. The provisional map is
  `.anechoic_tmp/ca-p-3073/current-family-rebind/active-preview-id-map.tsv`.
- [x] Freeze the compact ID map for the verified migration set. Keep the
  original path for ambiguous legacy exact references.
- [x] Apply the same map to Atom IDs and references in native YAML,
  filenames, and relations admitted by CA-P-3089. Keep unresolved
  relation occurrences in the migration receipt.
- [x] Verify the Active preview against the production native runtime.
  The preview contains 3,544 Active Atoms and 189 required Current
  records. The runtime resolved all 3,733 path-bound legacy aliases,
  loaded 45 Manifests, and read 12 Settings groups. The preview uses
  provisional IDs. The receipt is
  `.anechoic_tmp/ca-p-3073/active-native-startup/active-complete-preview-synthetic.json`.

### Project structure cutover

Keep the live legacy tree at `.anechoic_anechoic/` throughout staging and
the pre-cutover Local Release. Prioritize Active Atoms and their required
references. The archive may remain partial.

- [x] Preserve 293 unresolved archived source files in `.anechoic_archive/`.
  Their bytes match the current legacy sources. The legacy package selector
  excludes the archive and still selects the same 1,108 source files.

- [x] Create `.anechoic_new/` for native staging.
- [x] Stage the verified native records in `.anechoic_new/` with CA-P-3075.
- [x] With both trees present, verify that legacy Local Release still selects
  the protected inputs at their original paths and excludes the native
  staging tree from its package. Compare selected paths and digests with
  the protected baseline. The live selector check with the staging directory
  present matched all 1,108 selected source paths and digests. An isolated
  package check also excluded a native Manifest placed in the staging tree.
- [x] In an isolated checkout, rehearse the final names from CA-A-1461.
  Verify that the selected Project root resolves native SPEC, PMETA, and TKT
  and binds the native Project Manifest. Verify the native runtime entry
  points before the live rename. CA-P-3073 owns production wiring and
  CA-P-3096 verifies the migrated runtime. The production Docker launcher
  passed with a final-named native fixture and retained legacy Settings.

### Production native runtime

- [x] Build the delivered native model and relation rules from the reviewed
  CA-P-3089 packet. Bind CA-P-3075's final legacy reference map. The isolated
  loader uses the rehearsal's `native-aliases.json` row format.
- [ ] Review the 14 legacy relation types outside the CA-P-3089 packet.
  Keep them out of Workbench and MCP until the native model review is
  complete. Keep the CA-P-3075 migration evidence for each relation. The
  candidate declarations and replay are in
  `.anechoic_tmp/ca-p-3073/native-bridge-review/`.
- [x] Move all Project Settings into the Project Manifest. Preserve setting
  types and values in nested parameter groups. Keep the protected legacy
  Settings at their original path through the pre-cutover Local Release.
  The isolated Manifest rehearsal preserved 12 typed parameter groups and
  used the native name and prefix. See
  `.anechoic_tmp/ca-p-3073/project-settings-manifest-rehearsal.json`. Use the
  validated fields in `.anechoic_tmp/ca-p-3073/project-manifest-fields.json`
  when rendering the staged native Project Manifest. The isolated CA-P-3075
  renderer test produced 43 Manifests with rehearsal IDs. The reviewed native
  model validated the Project Manifest, and all parameter values matched.
  The `runtime` group carries the declared Workbench schema and retention
  settings. The launcher uses its existing defaults for settings the
  Project does not set.
  See `.anechoic_tmp/ca-p-3073/settings-renderer-rehearsal/`. Apply the inputs
  with the shared allocation when CA-P-3075 stages the native batch.
- [x] Wire production MCP and Workbench entry points to the validated native
  Manifest. The normal launcher selects it after the directory rename.
  Preserve the legacy Local Release selection during coexistence. Commit
  `189f757401` wires native queries, Workspaces, Views, and saved items.
  Commit `4dba891959` selects the Active Project Manifest from the
  Project’s `SPEC/` directory.
- [x] Verify the production launch and query path in an isolated checkout with
  the final directory names. Use CA-P-3096 to verify the migrated records and
  reference lookups. The isolated launch returned `READY_STARTED`, resolved
  a legacy alias through MCP, and fetched a native record through a Workbench
  View. With the 12 Manifest parameter groups, the browser displayed the
  native result and identified the source index as a startup snapshot. The
  isolated fixture used a separate MCP port. Commit `65897c1f7a` uses the
  Manifest for native Workbench schema mode and saved links. Verify the
  final migration data and relation bindings before closing this task.

### SPEC carrier directories

- [x] Identify the nested trial paths that belong to the SPEC cutover.
  Git verifies the indexed source bytes for all 84 trial drafts found in the
  legacy tree. The CA-P-3075 dry render has 85 nested sources, including a
  separate supporting Definition, and no nested trial destination. See
  `.anechoic_tmp/ca-p-3073/trial-cutover-audit.json`.
- [ ] Fix the confirmed nested trial paths before applying the SPEC carrier
  directory rules in CA-A-1466. Check the final staged output before
  changing any carrier paths.
- [ ] Verify that Active SPEC carriers use enabled lens directories in the owning
  Component Spec Section and that Draft and Archived carriers use the section’s
  `draft/` and `archived/` directories. Coordinate any carrier moves with
  CA-P-3075 after the affected Component paths are set.

### Technical cleanup

- [x] Inventory candidate technical files and directories for cleanup. The
  old top-level code directory is absent. The retained local artifacts have
  927 bytecode files with corresponding source in the moved code tree. Two
  records in former Analysis folders are protected release inputs. See
  `.anechoic_tmp/ca-p-3073/technical-cleanup-inventory.json`.
- [ ] Check references, Local Release inputs, and recovery dependencies for
  each candidate.
- [ ] After the affected moves and checks are complete, remove only verified
  obsolete items. Keep protected legacy inputs while the build depends on them.
  Commit `54043f9e4a` removed seven obsolete Playwright error reports and their
  run index after the C14 code move. The retained copies match the last
  tracked bytes in `.anechoic_tmp/ca-p-3073/retained-playwright-output/`.

### Integrated verification and cutover

Keep each Local Release run isolated. Use the integrated changes from the
work groups above.

- [x] With the legacy tree at `.anechoic_anechoic/` and the native tree at
  `.anechoic_new/`, run the full test gate and a clean Local Release in
  `refresh` mode. CA-P-3095 owns the clean legacy rebuild proof. CA-C-758
  permits a free port for the isolated startup check after the rebuild and
  protected input digests pass with the original Settings.
- [x] Verify `existing` mode with the generated assets saved with the matching
  checkout.
- [ ] After the pre-cutover Local Release succeeds, rename the live legacy tree
  from `.anechoic_anechoic/` to `.anechoic_legacy/` as one complete tree,
  including the legacy release inputs. Then rename `.anechoic_new/` to
  `.anechoic_anechoic/`.
- [ ] Verify discovery and reference lookup from the final native path.
- [ ] Verify Workbench and MCP `query_run` against the resulting runtime.

### Staged records and release checks

The staged native tree contains 5,683 Current Atoms, including all 3,544
Active Atoms, 727 Drafts, 3 archived CA-C-453 revisions, and 45 Manifests.
The Project Manifest carries 12 typed Settings groups.

The shared ID map has 5,999 old and new ID pairs. The native index resolves
6,413 original paths, including the two legacy CA-C-453 Version 1 paths
that map to different native Versions. The migration updates native YAML
identities, filenames, and 1,667 Atom container references. The native
index derives the matching CONTAINS relations. Legacy relation types
outside CA-P-3089 remain excluded until model review.

Anatoly approved retaining 169 unresolved Drafts in `.anechoic_legacy/`.
Both Local Release modes passed all 312 test modules and matched all 1,108
protected inputs. The isolated launcher selected the native Manifest at
the final path. MCP queries and Workbench verified the staged data. The
native MCP currently serves queries and Workbench from a startup snapshot.
Keep the legacy MCP live until native Atom Lifecycle and Workflow commands
pass verification in the isolated checkout.

The Change Current Status definitions stay in SPEC. They bind the direct
native status command. PMETA holds the Local Release and Public Release
Workflows. Mechanical migration preserves each Draft and its `-draft`
qualifier.

The staged validation and map are in
`.anechoic_tmp/ca-p-3073/combined-native-batches/candidate-002/`. The release
and isolated cutover receipts are in
`.anechoic_tmp/ca-p-3073/isolated-release-port/`.

## References

CA-A-1461, CA-A-1462, CA-A-1466, CA-C-749, CA-P-3075, CA-P-3076,
CA-P-3078, CA-P-3095, and CA-C-758.
