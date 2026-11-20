---
atom_family: TKT
atom_id: AN-T-1803
structure:
  container:
    atom: AN-T-1804
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 2
  updated_at: 2026-11-09 00:18:04 +0400
---

## Summary

Wire relation metadata into release packages

## Details

Release packaging generates and seals canonical relation metadata before image construction. Missing, failed and unsafe outputs are rejected. Local release 003 verified the installed asset. New schema-package integration remains under P2752.
