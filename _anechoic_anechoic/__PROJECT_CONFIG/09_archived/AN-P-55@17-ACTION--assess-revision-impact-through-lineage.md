---
atom_family: PROJECT_CONFIG
atom_id: AN-P-55
structure:
  container:
    component: C9
context:
  template: action
state:
  status: archived
  version: 17
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Assess revision impact through lineage

# Summary

Assess revision impact through lineage

## Operation

Assess Lineage Impact **means** the reusable Action that assesses **every** reachable descendant lineage branch of **`=1`** changed Atom **until** **every** branch has an explicit impact disposition.

apply this Action **when** the Atom:

- receives a new accepted Revision;
- is replaced by a successor; **or**
- moves **to** the archive.

an Operator **or** AI Agent performs this Action within its existing authority. the assessment follows the existing lineage recursively; it does **not** create another cross-Scope Unit dependency graph.

## Details
