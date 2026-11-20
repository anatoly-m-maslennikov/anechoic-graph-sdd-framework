---
atom_family: TKT
atom_id: AN-T-2376
structure:
  container:
    component: C00
  priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: 2026-10-04 14:13:37 +0000
---
# Summary

Retain the f04 rollup checker recovery

## Concern

The F04 rollup helper generated CA-P1401 instead of CA-P-1401, so its first membership equality check failed. This was an auxiliary identifier-normalization bug, not a source mismatch or a passed check.

## Evidences

A1067 retains the first failed check at13:59:43 UTC and the corrected same-scope passing check at14:00:17 UTC. All37 primary memberships, five aliases, two prior receipts and three unchanged Done children were then checked. No failed result is counted as accepted.

## Blast radius

Only the stated auxiliary diagnostic and its truthful evidence receipt. Required independent acceptance, source authoring and runtime proof remain separate; no gate is waived or automatic rerun campaign created.
