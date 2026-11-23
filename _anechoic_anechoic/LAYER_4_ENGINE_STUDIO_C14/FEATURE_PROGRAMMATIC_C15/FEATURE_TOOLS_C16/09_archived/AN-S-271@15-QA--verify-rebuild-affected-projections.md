---
atom_family: SPEC
atom_id: AN-S-271
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 11:29:41 +0400
---
## Summary

Verify rebuild affected Projections

# Verify rebuild affected Projections

## Claim checked

CA-M-255 derives **every** affected Projection, materializes **only** approved outputs **in** dependency order, **and** verifies currentness **and** idempotence.

## Applicable when

apply whenever affected-Projection derivation, dependency ordering, preview approval, currentness, **or** idempotence handling changes.

## Test case

inspect the registered `PROJECTION_REBUILD` unit, **then** use changed source frontiers that affect one upstream Projection **and** one dependent Projection. preview, approve, **and** rebuild them, **then** rebuild against the unchanged frontier **and** compare outputs; repeat with the dependent Projection omitted from the affected set.

## Acceptance criteria

`PROJECTION_REBUILD` has prefix `PROJECTION_REBUILD`, immediate `TOOLS` owner, `unordered_unit` kind, Structural level `4`, address `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/PROJECTION_REBUILD`, **and** realization path `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/PROJECTION_REBUILD/`. the valid case previews **and** materializes both affected outputs **in** dependency order with source-frontier provenance; the repeated build is identical **and** current. the incomplete affected set produces no accepted publication.

## Failure disposition

reject the realization **and** preserve changed frontiers, dependency graph, preview, approvals, output provenance, repeated-output comparison, **and** incomplete-set finding.
