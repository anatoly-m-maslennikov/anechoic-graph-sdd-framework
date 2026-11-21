---
atom_family: TKT
atom_id: AN-T-1815
container:
  atom: AN-T-1818
priority: 2
context:
  template: work_report
state:
  status: done
  version: 3
  updated_at: 2026-11-09 01:40:38 +0400
---

## Summary

Apply the schema specification

## Details

Five schema specifications are Current. Header and Content SQL names use dotted paths with snake_case segments; Mode 2 is configured explicitly. The real generator has 19 declared Header columns, 62 observed columns and six Content columns. Mode 1 admits valid source rows and skips incompatible ordinary sources with diagnostics, retaining strict structural/transaction failures. Cached ordinary deltas remain bounded and provenance writes follow commit. Independent reviews and eight Docker E2E cases pass; live deployment remains P2731.
