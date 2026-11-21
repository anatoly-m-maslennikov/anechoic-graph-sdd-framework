---
atom_family: SPEC
atom_id: AN-S-1029
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-11-07 15:28:42 +0400
---

## Summary

Encode configuration surfaces in owning Atoms

## Claim

### Prose Claim

An owning Atom may carry its defined machine-readable properties in YAML frontmatter. Its ordinary RMED Claim is a zero-value container with one or both Formal Claim and Prose Claim children, each with zero or one Markdown values. A Formal Claim value contains a CFEL-labelled fence. Frontmatter is not a second Claim or independent source. Project initialization inputs and applicable ANECHOIC behavior and configuration choices belong to Project Settings; The Project structural declaration belongs to its Scope Unit Declaration Atom; a non-Project Scope Unit’s structural declaration belongs to its Scope Delegation Atom.
