---
atom_family: SPEC
atom_id: AN-S-2749
container:
  component: C9
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 16
  updated_at: 2026-10-21 01:47:52 +0400
---
## Summary

Derive Atom Subjects Graph from Current Atom Subjects

# Summary

Derive Atom Subjects Graph from Current Atom Subjects

## Scope

Atom Subjects Graph derivation from current Atom Subjects.

## Claim

**to** derive an Atom Subjects Graph, the Generator **must** reproduce **every** selected Subject as a direct GOVERNS **or** DEPENDS_ON graph link from its source Atom **to** its target with its exact canonical Subject Target, Subject Path, **and** Relation Kind **without** adding authority, requiring a duplicate target-kind field **in** the Atom's Subjects, **or** creating a separately identified Subject object. a Projection **may** derive a target's kind from its canonical authority **when** the Projection's own Spec calls for that classification; it **must not** independently reauthor that kind **or** require it as duplicated source Subjects metadata. an Atom Subjects Graph may include Entity-root and Method-root Subject Targets. an Entities Graph view must include only Entity-root targets unless its own Spec explicitly admits a distinguishable external reference. an unmigrated temporal Carrier admitted temporarily by CA-D-269 retains its source classification as migration evidence **without** changing the direct reference **or** requiring that classification **in** the canonical flat representation.

## Details
