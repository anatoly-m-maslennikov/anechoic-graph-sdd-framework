---
atom_id: CA-D-634
ref_id: CA-D-634
container:
  scope_unit: CA-SU-11
role: Delivery
form: Decision
topics:
  main_subject: ANECHOIC_MODEL <+ Projection/(.Form:=Entities Graph)
  dependencies:
  - ANECHOIC_MODEL <+ Entity
  - ANECHOIC_MODEL <+ Relation
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Projection/(.Form:Entities Graph)
  - ANECHOIC_MODEL <+ Projection.Updated At
  - ANECHOIC_MODEL <+ Carrier/Directory
tier: 5
status: Active
version: 23
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-D-634-CORE_META_MODEL-DECISION--deliver-readable-entities-graph-trees-as-markdown.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-634-CORE_META_MODEL-DECISION--deliver-readable-entities-graph-trees-as-markdown.md
  source_atom_id: CA-D-634
  source_atom_revision: 23
  source_sha256: ac8a14b0302d0b90617d52a74ec69afea644e54a93b8b0d03a20e39b66579c4e
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Deliver readable Entities Graph trees as Markdown

## Claim

### Prose Claim


The Markdown Carriers for readable Entities Graph structural and named declaration views.


Deliver the view as a UTF-8 Markdown file under the Project's declared Projection root. Include YAML frontmatter and tab-indented trees inside fenced text blocks.

## Details

Use these frontmatter fields:

- `artifact_form: Projection`
- `projection_id`, `named_selection` and `source_of_truth`: under CA-D-635. Use its filename convention and retain the Projection ID under CA-R-1943.
- `type: Entities Graph`
- `updated_at`: actual latest completed rebuild time in Project time, with an explicit UTC offset, under CA-D-310.
- `sources`: the complete deduplicated list of contributing Atom references in `CA-N-123@M` form, where N is the Content Role letter and M is the numeric Version. Sort the references alphabetically. This is the Projection's source list, not its Atom ID.

Declare the requested source selection and any narrower display selection in the document. When non-Atom sources also contribute, identify their exact source evidence separately; do not invent Atom IDs for them.

Inherency view body order:

1. `## Inherency tree`
   - `### Primary entities`: main tree without dependents.
   - One `### <qualified entity name>` section per primary entity with dependents, in first-appearance order from the main tree.

Use one literal tab per tree depth inside fenced `text` blocks. Use spaces, not tabs, for YAML indentation. Keep readable entity names, not YAML storage-key spellings. Preserve relation distinctions with the admitted compact notation or explicit relation labels; indentation alone must not erase edge meaning.

A source-derived tree remains a Projection, not a new source of truth. This format does not require changing unrelated graph exports.

### Declaration-view delivery

The selected Relation Type declaration view uses the same Entities Graph Type, its own named selection and a stable Projection ID under CA-R-1943. Reuse CA-D-635's filename and YAML fields. Render named Relation Types with defining Atom IDs, their meanings and explicitly declared direction, inverse, derivation or transitivity. The defining Atom has Status; the Relation Type has no Status field. Do not turn actual endpoint tuples into Type declarations.

The model views contain primary entities, then one property section per primary entity with properties, including inherited properties marked `[inherited]`. Keep primary-kind definition references as Atom IDs rather than copied definition text. Source-declared containment and specialization retain their distinct operators; use spaces around the complete containment operator, for example `>{1+} Atom/(.Header.Role := Operations)/(.Header.Form := Step)`.

Report missing definitions, unresolved identities, unsupported source syntax and coverage limits explicitly. Do not create a separate Graph Rule instance catalogue or render retired frontmatter `claim.*` grammar. Constraints and simple formal expressions belong to the corresponding Entity Definitions. Keep source selection, complete contributing source versions and actual rebuild timestamp in every Projection.
