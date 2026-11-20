---
atom_family: TKT
atom_id: AN-T-1836
structure:
  container:
    atom: AN-T-1846
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-09 00:18:04 +0400
---

## Summary

Generate relations during image builds and local release

## Details

Image and local-release paths regenerate canonical relation metadata, seal it in input identity and reject missing or failed generation. Local release 003 installed 0.4.4.39. Schema-asset additions remain separate unfinished work under P2752.
