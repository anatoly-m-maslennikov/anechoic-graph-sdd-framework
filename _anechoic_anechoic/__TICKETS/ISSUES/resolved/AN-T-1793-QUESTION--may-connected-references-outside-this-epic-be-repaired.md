---
atom_family: TKT
atom_id: AN-T-1793
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

May connected references outside this Epic be repaired?

## Concern

Two reviewed Engine merges have three Current callers outside the migration scope. Core Delivery D366 cites D594 twice for the Project MCP port contract. Old DISCOVER_TOOLS Delivery D512 and Evaluation E525 each refer to D678 in their Header and content.

The proposed repair replaces those references with the surviving R1901 and R2785 contracts, preserving the callers' behavior, Summary, Form, Scope Unit, Tier and Status. The repeated R2785 citation in E525 becomes one citation. Normal Version updates and predecessor archives still apply. No other Core or old Tool migration, code change or runtime acceptance is included.

## Details

The Operator approved the reference-only repairs in D366, D512 and E525. D594 references are replaced by R1901; D678 references are replaced by R2785, with the repeated R2785 citation in E525 deduplicated. Their behavior, Summary, Form, Scope Unit, Tier and Status stay unchanged. Each repair receives its next Version and a predecessor archive.

This resolves the scope question only. It does not authorize any other Core or old Tool migration, code change, runtime acceptance or release. The repair preview and application receipts are in .anechoic_tmp/engine-summary-merge-20261109.
