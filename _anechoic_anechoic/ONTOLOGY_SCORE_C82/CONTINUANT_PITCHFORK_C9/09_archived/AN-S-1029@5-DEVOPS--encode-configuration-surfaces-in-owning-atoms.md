---
atom_family: SPEC
atom_id: AN-S-1029
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T22:32:20.313346+00:00"
---

## Summary

Encode configuration surfaces in owning Atoms

## Claim

An owning Atom may carry its defined machine-readable properties in YAML frontmatter. Its ordinary Claim is a zero-value container with one or both Formal Claim and Prose Claim children, each with zero or one Markdown values. A Formal Claim value contains a fence labelled for its formal language. Frontmatter is not a second Claim or independent source. The Project Manifest owns Project settings; Component Manifests own Component structural declarations.
