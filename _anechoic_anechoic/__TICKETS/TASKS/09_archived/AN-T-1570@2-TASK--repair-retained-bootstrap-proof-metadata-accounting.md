---
atom_family: TKT
atom_id: AN-T-1570
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:38 +0400
---
## Summary

Repair retained bootstrap proof metadata accounting

# Summary

Repair retained bootstrap proof metadata accounting

## Objective

Restore exact persistent-inventory verification of the retained bootstrap image proof while preserving installed N and all proof bytes.

## Details

Use the existing inventory-defined ephemeral exclusion only after unsafe-carrier and secret-path refusal. Preserve exact persistent contents, modes and extra-file rejection in both context digest and package-context readers. Do not alter N, rewrite its evidence or replay N7. This bounded repair reuses current inventory authority and the Operator's instruction to ignore Finder metadata; it adds no Workflow or independent registry.

## Definition of Done

Metadata-only retained proof reopening succeeds without mutation; secret-shaped ephemeral files and arbitrary extra persistent files still refuse; focused regressions pass. Fresh actual Release gates remain separate.

## Results

N7 stopped before the Unit suite because five Finder files changed its raw retained proof-context digest. Excluding those files recovers the exact already-recorded digest. Both readers now share unsafe → secret refusal → ephemeral exclusion ordering. Thirteen bootstrap-image tests pass, including preserved metadata, `.env.pyc` refusal and arbitrary extra-file refusal. The actual retained N proof reopens as verified with the unchanged N manifest and immutable image. No N or proof files were modified.
