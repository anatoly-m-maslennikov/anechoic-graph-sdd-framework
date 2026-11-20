---
identity:
  atom_id: AN-S-501
context:
  container:
    component: C9
  tier: 1
  lens: DevOps
state:
  status: active
  version: 32
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Carry Projected Atoms without New Identity

## Claim

### Prose Claim


The source binding and representation of each Atom Carrier projected as an Applicable Methodology member.


Applicable Methodology **must** represent each projected Atom Carrier with a one-way source binding **to** its selected authoritative Atom Revision **without** creating another Atom identity:

- preserve the source Atom's authored Frontmatter **and** Main Content unchanged; the **only** compiler-added block is the source binding below.
- store **`=1`** `projection.source_carrier_path` value **in** the projected Carrier's Frontmatter. resolve it relative **to** the projected Markdown file's directory **to** the original Atom Carrier **in** the selected Methodology Sources.
- retain the source Atom ID **and** Version; together with the source binding, they identify the selected source Revision. verify source fidelity under CA-E-379 rather than assuming that an existing path proves currentness.
- treat this block as Projection metadata, **not** an authored Atom Property **or** a new Atom-to-Atom Relation. do **not** copy it upstream **or** add inverse links **to** source Atoms.

**after** removing **only** the generated source-binding block, the projected Carrier bytes **must** equal the selected source Carrier bytes. missing, ambiguous, wrong-source, **or** stale bindings **must not** be accepted as current Applicable Methodology.
