---
atom_family: SPEC
atom_id: AN-S-63
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Select the project frontier during reconciliation

# Select the project frontier during reconciliation

## Test case

Given admitted, ignored, pipeline-owned, **and** ambiguous repository paths, **when** the background reconciliation worker observes the frontier **and** the pure manager classifies its typed facts, **then** ordinary Git-eligible files **and** .anechoic files are eligible, Git-ignored paths **and** top-level dot-directories other than .anechoic are excluded, pipeline-owned Journal **and** Runtime writes are correlated rather than admitted as new subjects, **and** ambiguous ownership becomes blocked. COMMIT_TRIGGER performs no frontier scan.

## Sources

- [CA-M-087 — Process one project-path action](../../05_method/CA-M-087-TOOLS-CORE-IMPL_METHOD--process-one-project-path-action.md)
