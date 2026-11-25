---
atom_family: TKT
atom_id: AN-T-3915
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 4
  updated_at: '2026-11-24T12:50:44.702322+00:00'
---
## Summary

Recall historical bugs from detached checkouts

## Work

Add an automated historical checkout-analysis stage to the golden corpus. Seek high recall across the 14 linked session candidates using actual detached checkouts of the old and fixed revisions. Bounded extra historical findings are acceptable. New scanner inputs are historical only; do not review current runtime.

Require exact historical source or a valid archived receipt for each claimed old and fixed state. Preserve provenance, commands, evidence, and the analysis outcome. Treat missing pairs and unsupported analysis as coverage gaps, not passes. Await measured results before claiming outcomes.

Known pending gaps are exact buggy source for native Compose failing selection state, overlapping workflow guards and closed graph, and state analyzer namespace imports.

## Acceptance

The automated stage records coverage of the 14 linked candidates and any bounded additional findings. Each supported result has traceable old and fixed evidence from exact historical source or valid archived receipts. Missing pairs, unsupported cases, and unresolved recall gaps are explicit; no unsupported case is counted as a pass.

## Findings

All ten original frozen cases now have source-derived checkout analyzers. The combined run found 20 of 20 targets on detached Git old revisions. Three additional hash-verified archived or mixed pairs bring the total to 23 of 23. All 23 corresponding fixes had zero target findings and no target was unresolved.

The results cover 11 of the 14 distinct original session candidates. The ten added analyzers cover separate corpus cases; they do not increase that candidate count. Watcher wake-up and receipt are split into two pairs, and a distinct SQL keyword-case dependency replay is additional.

Peak output was six findings per checkout, including at most five extra indications. Those extra indications remain untriaged. The corpus is `LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/golden_bugs`; two checkout scripts are next to it.

Exact buggy source remains missing for native Compose failing selection state, overlapping workflow guards and closed graph, and state analyzer namespace imports. These are coverage gaps, not passes. Keep this Task in queue.

Evidence: `$BB_THREAD_STORAGE/all-corpus-replay.json`, `$BB_THREAD_STORAGE/all-corpus-archived-summary.json`, and `$BB_THREAD_STORAGE/all-corpus-frozen.log`.
