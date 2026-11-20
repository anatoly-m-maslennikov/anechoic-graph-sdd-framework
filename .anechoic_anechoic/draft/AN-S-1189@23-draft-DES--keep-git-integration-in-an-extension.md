---
identity:
  atom_id: AN-S-1189
context:
  container:
    component: C00
  tier: 1
  lens: DES
state:
  status: draft
  version: 23
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Keep Git integration in an Extension

## Claim scope

Git integration in the Core Meta-Model.

## Claim

Git integration **must** be optional Extension authority, **not** a prerequisite of the Core Meta-Model. Git commit policies, commit-message encodings, hooks, **and** event-to-commit references belong **to** that Extension; selecting it **must not** replace the authoritative Journal **or** make Git history an independent source for the same recorded facts. the Core Meta-Model **must** remain applicable **without** Git integration.
