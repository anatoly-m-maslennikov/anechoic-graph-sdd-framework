---
atom_family: TKT
atom_id: AN-T-2113
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 04:34:49 +0400
---

## Summary

Verify Workbench fixtures and bulk writes

## Details

Updated stale fixtures for canonical Atom filenames, current dotted Header columns, `relative_path`, first-loaded duplicates, declared audit tables and result-file/inline response contracts. The final Workbench host suite passed 275 tests with three opt-in live canaries skipped. Docker tests remain separate. Four focused insert tests also pass after checking rollback in both small and bulk paths.

Full and incremental public projection writes now reuse one insert helper. Batches up to eight rows retain the existing row path; larger batches use native columnar insertion. A three-sample host benchmark at 2,292 columns measured 128 rows at 5.204s before and 0.292s after, with exact value equality. This is insertion-phase evidence, not image, end-to-end throughput or resource acceptance. No schema semantics or source Atom data changed.

Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2866/fixture-refresh-20261111/host-suite-final.log`, `final-source-hashes.json`, and `wide-insert-20261111/final_metrics.json`. Model-source clarification, generic inheritance support and final image/canary/performance checks remain open under P2866/P2813/P2817/P2818. The healthy serving image was preserved.
