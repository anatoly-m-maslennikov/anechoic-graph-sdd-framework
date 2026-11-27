---
atom_family: SPEC
atom_id: AN-S-501
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C15
tier: 1
context:
  lens: DevOps
state:
  status: active
  version: 36
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Carry Projected Atoms without New Identity

## Claim

### Prose Claim


The source binding and representation of each Atom Carrier projected as an Applicable Methodology member.


Use AN-S-1999 and AN-S-2134 for Carrier and Projection semantics. Bind each projected Applicable Methodology member to its exact source revision.

- preserve the source Atom's authored Frontmatter **and** Main Content unchanged; the **only** compiler-added block is the source binding below.
- store **`=1`** `projection.source_carrier_path` value **in** the projected Carrier's Frontmatter. resolve it relative **to** the projected Markdown file's directory **to** the original Atom Carrier **in** the selected Methodology Sources.
- retain the source Atom ID **and** Version; together with the source binding, they identify the selected source Revision. verify fidelity against the selected source Revision rather than assuming that an existing path proves currentness.
- treat this block as Projection metadata, **not** an authored Atom Property **or** a new Atom-to-Atom Relation. do **not** copy it upstream **or** add inverse links **to** source Atoms.

**after** removing **only** the generated source-binding block, the projected Carrier bytes **must** equal the selected source Carrier bytes. missing, ambiguous, wrong-source, **or** stale bindings **must not** be accepted as current Applicable Methodology.
