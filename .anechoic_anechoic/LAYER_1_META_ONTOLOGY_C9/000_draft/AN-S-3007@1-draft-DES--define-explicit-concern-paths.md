---
atom_family: SPEC
atom_id: AN-S-3007
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:45.234594+00:00'
---
## Summary

Define explicit Concern paths

## Claim

### Prose Claim

An explicit Concern uses three fields: `concern.path` identifies the full existing path, including every intermediate type; `concern.subject` names what the Atom addresses; and `concern.relation` names the relation from the subject to the path in snake case. In a path `/` expresses containment and `//` expresses that the following type is narrower than the preceding type. Validate every path hop against the corresponding existing relation. A structural Concern may instead be supplied by the Component tree: a child Component's Purpose and Manifest are in the parent and address the child; a Contract may use its containing Component implicitly.

## Details

Acceptance: `path: Model/Graph/Node//Artifact`, `subject: atom`, `relation: narrower_than` is valid when Model contains Graph, Graph contains Node, Artifact is narrower than Node, and atom is narrower than Artifact. Reject it if either containment hop or the narrowing hop is absent; reject an incomplete path that omits Graph. These path relations do not replace the Atom's `contained_by` relation.

Sources: CA-A-1462@1-draft, CA-P-3081@1. Task: CA-P-3081.
