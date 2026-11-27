---
atom_family: SPEC
atom_id: AN-S-275
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C37
tier: 1
context:
  lens: DES
state:
  status: active
  version: 24
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Persist reproducible non-authoritative Entity and Term graph Projections

# Persist reproducible non-authoritative Entity and Term graph Projections

`GENERATE_ENTITY_GRAPH` **must** accept one explicitly selected folder **or** equivalent source frontier **and** derive one reproducible, non-authoritative Projection. The result **must** contain **every** declared Term found **in** the parseable frontier; each Term's direct parent **when** declared; the direct dependency graph; the complete dependency-Term closure; cycles **and** relation-cardinality violations; source Carrier path **and** digest lineage; unknown **or** unparseable regions; the selected frontier identity; **and** an explicit non-authoritative status.

Identical readable source bytes **and** settings **must** produce byte-identical semantic output **in** stable order. Unknown **or** unparseable regions remain visible **and** **must not** be silently omitted, repaired, **or** interpreted as absence. A cycle **or** cardinality violation is reported as projection data **and** a failed validation disposition, never repaired by changing authority.

Description **and** ordinary generation are mutation-free. Persistence occurs **only** **when** the caller supplies an explicit output path **or** a registered Project setting resolves one unambiguous Projection destination. One output Carrier represents exactly one source frontier **and** is replaced atomically. The Tool **must** reject destinations inside governed Atom **or** Journal authority, path traversal, symlink escape, ambiguous configured destinations, **and** **any** request that would make the Projection authoritative.

the persisted Projection is suitable for strictly read-only consumption by `WORKBENCH` and optional presentation by `GRAPH_UI`, but it has no authority of its own: current Atoms, Journals, authoritative Settings Artifacts, **and** **any** other authority admitted by the applicable methodology remain authoritative independently of the Projection.

### Readable Markdown export

Keep a registered output's Projection ID across rebuilds. Require the existing ID and matching display and source selections before replacing its Markdown Carrier. A separate display can have its own ID. Use the renderer's registered filename under the Project `_projection/` folder.

Carry `artifact_form`, `projection_id`, `form`, `source.named_selection`, `source.atoms`, and `updated_at` in YAML frontmatter. Use Map for tree exports and Catalog for the Relation declaration export. List contributing Atom revisions, name the source and display selections, and render tree indentation inside a text fence.
