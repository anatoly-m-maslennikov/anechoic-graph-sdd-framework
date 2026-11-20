---
atom_family: SPEC
atom_id: AN-S-63
structure:
  container:
    component: C16
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 26
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Select the project frontier during reconciliation

# Select the project frontier during reconciliation

## Test case

Given admitted, ignored, pipeline-owned, **and** ambiguous repository paths, **when** the background reconciliation worker observes the frontier **and** the pure manager classifies its typed facts, **then** ordinary Git-eligible files **and** .anechoic files are eligible, Git-ignored paths **and** top-level dot-directories other than .anechoic are excluded, pipeline-owned Journal **and** Runtime writes are correlated rather than admitted as new subjects, **and** ambiguous ownership becomes blocked. COMMIT_TRIGGER performs no frontier scan.

## Sources

- [CA-M-087 — Process one project-path action](../../05_method/CA-M-087-TOOLS-ENG_DECISION--process-one-project-path-action.md)
