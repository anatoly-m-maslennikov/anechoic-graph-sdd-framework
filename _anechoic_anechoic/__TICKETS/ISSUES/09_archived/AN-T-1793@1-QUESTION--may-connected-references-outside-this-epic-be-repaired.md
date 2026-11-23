---
atom_family: TKT
atom_id: AN-T-1793
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 20:33:41 +0400
---

## Summary

May connected references outside this Epic be repaired?

## Concern

Two reviewed Engine merges have three Current callers outside the migration scope. Core Delivery D366 cites D594 twice for the Project MCP port contract. Old DISCOVER_TOOLS Delivery D512 and Evaluation E525 each refer to D678 in their Header and content.

The proposed repair replaces those references with the surviving R1901 and R2785 contracts, preserving the callers' behavior, Summary, Form, Scope Unit, Tier and Status. The repeated R2785 citation in E525 becomes one citation. Normal Version updates and predecessor archives still apply. No other Core or old Tool migration, code change or runtime acceptance is included.

## Details

Await the Operator's scope decision. Until then, keep D594 and D678 Current and hold their two merge groups; continue unrelated groups. The concrete six-reference preview is recorded in .anechoic_tmp/engine-summary-merge-20261109/external-reference-repairs.diff. No outside-scope caller has been edited.
