---
atom_family: SPEC
atom_id: AN-S-2573
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T23:08:40.599061+00:00"
---
## Summary

Select Subject Graph views by Scope Units and branches

## Claim

### Prose Claim


Each focused Subject Graph Projection **must** state and use one declared selection. Scope Unit criteria select Current RMEDO source Atoms by their Local Scope Unit, with an explicit option to include descendants declared in Project Structure. Folder nesting does not determine the selected Scope Units. Subject-branch criteria select canonical target branches while retaining ancestor context and the source-backed properties needed for inheritance within the selected source set.

Multiple selected Scope Units form a union; multiple selected branches form a union. When both criteria are supplied, both restrictions apply. With neither restriction, use all Current RMEDO sources. The Projection Type determines its view, not which sources are selected.

For dependency-only results, compare exact Depends On and Governs paths inside the same selected source set. Do not silently consult sources outside that set to suppress entries. Namespace and Subject operator boundaries remain significant; a lexical prefix such as Atom must not also match AtomExtra.

## Details

The Projection records its Scope Unit and branch criteria, descendant option, named selection and source-of-truth identity. Its YAML sources list records the actual supporting source IDs and Versions. Branch views retain declared inherited-property context without claiming that omitted branches were rendered. Source and target filters do not create another entity or copy the selected members.
