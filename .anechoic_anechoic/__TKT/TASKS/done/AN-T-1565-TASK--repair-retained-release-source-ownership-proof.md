---
identity:
  atom_id: AN-T-1565
context:
  container:
    atom: AN-T-1578
  tier: 3
  template: task
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Repair retained Release source ownership proof

## Objective

Resolve the exact source-delivery ownership failure before a fresh Release Version Run.

## Details

1. Read N6's terminal checkpoint and diagnose the retained executing-N proof and current source-copy differences separately.
2. Repair confirmed defects with focused regression tests and independent acceptance.
3. Preserve installed N, its selector, the existing delivery and retained predecessor trees. Do not bypass ownership checks or replay N6.

Root owns Git integration and runtime effects. Estimated diagnosis/repair slice <=15 minutes; unrelated release gates retain their existing Tasks.

## Definition of Done

The underlying failure is explained, the accepted repair passes focused regression tests, and a fresh source-bound Run may attempt delivery without weakening ownership or currentness checks.

## Pre-execution review

The terminal N6 checkpoint and CA-C-491 establish the gap. Operator authority, preservation of valuable information and installed-N rollback require proof before replacement, not an overwrite.

## Acceptance evidence

The exact failure is four ephemeral Finder files in retained N. The current delivery differs from canonical sources only in ephemeral metadata, so corrected selection is a no-op, not predecessor replacement. The existing inventory rule is reused after unsafe-carrier rejection; arbitrary extra persistent files, hash/mode changes and incomplete predecessor copies still fail closed.

Thirty-four focused delivery, packaging and bootstrap tests pass. Independent read-only acceptance verifies the narrow change, including secret-path refusal before ephemeral exclusion. No installed-N or delivered-tree mutation occurred, and N6 was not replayed. Fresh Run gates remain separate work.
