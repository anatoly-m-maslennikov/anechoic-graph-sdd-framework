---
atom_family: SPEC
atom_id: AN-S-2338
container:
  component: C9
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 12
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Serialize Projection identity and filenames

# Summary

Serialize Projection identity and filenames

## Scope

Projection Markdown File Carriers.

## Claim

Use this filename:

`<PROJECT_PREFIX>-PROJ-<ID>-<CURRENT_SCOPE_NAME>--<PROJECTION_TYPE>--<NAMED_SELECTION>.md`

Store the full Projection ID as `projection_id` in YAML frontmatter. The filename and frontmatter must identify the same Projection.

## Details

For this Project, the prefix is `CA`. For example:

`CA-PROJ-001-CORE_META_MODEL--Entities-Graph--Current-Atoms.md`

Its full Projection ID is `CA-PROJ-001`; `001` is the ID segment in the filename. Use the current Scope Unit name, not its label.

The YAML frontmatter carries:

- `artifact_form: Projection`
- `projection_id`: the full Projection ID.
- `type`: Projection Type.
- `named_selection`: the named source selection.
- `source_of_truth`: an unambiguous reference to the authoritative source set.
- `updated_at`: the latest completed rebuild time under CA-D-310.
- `sources`: contributing Atom references with Versions, such as `CA-R-123@3`. Identify contributing non-Atom sources separately; do not invent Atom IDs for them.

Keep the ID under CA-R-1943 when rebuilding or changing only the Scope Unit name or Carrier path. Filename changes do not by themselves create a new Projection.

Type-specific Delivery rules define the body and any additional source evidence. Store the Carrier under the applicable Projection root under CA-D-550.
