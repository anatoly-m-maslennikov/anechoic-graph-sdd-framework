---
atom_family: TKT
atom_id: AN-T-3926
container:
  atom: AN-T-3904
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-26T10:47:43.730140+00:00"

---
## Summary

Review Continuant Pitchfork material and Manifest coverage

## Work

Review former E and QA material for retirement. Check current evidence and dependencies before retiring anything.

Review former M material. Retire superseded methods. Move current procedures to Occurrent Metronome. Split mixed material where a declaration must remain in Continuant Pitchfork.

Review former D only for filenames, paths, and admission of Markdown files and folders. Propose each rule in the Manifest of the entity it governs, such as Atom or Component. File and Folder define the carrier types.

Find missing Continuant Manifests. Record each needed Node, Property, or Relation and the rule it declares. Keep the Ontology engine-agnostic.

Review former R rules against the active Model Manifests. Carry forward rules by their owning Manifest. Check consumers before retiring superseded Specs.

## Decisions

Retire installed Extensions. Project Config Custom Model is the sole source of Project-specific Model declarations.

Retire the routing tree and Direct Route Skills. The `ane` Skill uses MCP tool discovery.

Properties name the types they accept. Atom Relations keeps one authored entry per Relation name with distinct Atom references.

Every folder that represents a child Component must end in an underscore followed by that Component's stable ID.

An Atom Companion Container uses its owning Atom's full filename without the `.md` extension.

An Atom's Header and Content are its source of truth. The authored `Header.Container` determines its containment.

Derive the expected Carrier filename and path from the Atom Header and Content Summary.

A Carrier has a placement discrepancy when its filename or path differs from the derived destination.

Declare the Atom Status Property and its allowed values in the Ontology's Formal Manifests.

When an authored SSOT Relation targets an Atom, use its stable Atom ID by default. Reserve exact revision IDs for History and Trace Relations. `IS_REPLACEMENT_FOR` targets a stable Atom ID. The two linked Atoms cannot both be Active.

### Engine behavior

Index the Atom under its declared Container. Record any placement discrepancy in the Project's Issues with the Atom reference and the actual and expected paths.

### Methodology

Declare Atom Status transitions in the `DOM/MTD` Lens in Occurrent Metronome.

Author replacement on a Draft. Each new predecessor must be Ready or Active. Archive the predecessor before publishing the replacement.

## Review Status

Four review subtasks are Done. The ledger records 1,037 exact revisions and their dispositions.

Keep the existing Actor declaration. The Actor kinds are Operator and AI Agent. Defer native Actor Manifests. Retire the legacy Name, event attribution, Primary Entity classification, and Framework Instance exclusion.

Keep the remaining active Event and Runtime dependencies for reconciliation with Workflow and the Journal. Prior archived revisions remain available as evidence.

## Acceptance

Identify exact Atom revisions and the evidence for each disposition. Name each proposed Manifest addition. Record uncertain cases for Operator review.

## Verification

All five subtasks are Done. The review ledger records the governing Model, consumer, or retirement decision for each exact revision.
