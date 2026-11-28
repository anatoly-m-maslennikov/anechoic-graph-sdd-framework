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
  status: archived
  version: 5
  updated_at: '2026-11-24T13:03:33.131379+00:00'
---
## Summary

Recall historical bugs from detached checkouts

## Work

Add an automated historical checkout-analysis stage to the golden corpus. Seek high recall across the 14 linked session candidates using actual detached checkouts of the old and fixed revisions. Bounded extra historical findings are acceptable. New scanner inputs are historical only; do not review current runtime.

Require exact historical source or a valid archived receipt for each claimed old and fixed state. Preserve provenance, commands, evidence, and the analysis outcome. Treat missing pairs and unsupported analysis as coverage gaps, not passes. Await measured results before claiming outcomes.

Include E2E and canary historical cases. The remaining source gap is the exact Compose integration scratch failing state; do not identify its Git parent as buggy without evidence.

## Acceptance

The automated stage records coverage of the 14 linked candidates and any bounded additional findings. Each supported result has traceable old and fixed evidence from exact historical source or valid archived receipts. Missing pairs, unsupported cases, and unresolved recall gaps are explicit; no unsupported case is counted as a pass.

## Findings

There are 28 verified historical pairs, covering 13 of the 14 distinct original session candidates. Measured cases have zero missed old targets and zero matching fixed target findings. Recovered namespace-import and workflow-guard captures pass exact old and detached fixed scans. The original frozen cases also have source-derived checkout analyzers.

Three additional golden replays each find the old target and clear the fix: storage-fallback SQL postcondition before dispatch (AN-T-3012, a harness gap; product cause remains open), release canary Backend coupling (`aaf926d0a8`), and isolated-port false rejection in release preflight (`0382528dcd`, host gate).

Across measured checkout scans, the maximum was six total findings and five extra indications per checkout. Extra indications remain untriaged. Exact Compose integration scratch source is still pending; this gap is not a pass.

E2E and canary observations below are evidence only; no synthetic replay is claimed:

- Missing pinned Chromium v1248 and Docker disk-full exit: `/Users/am/.bb/thread-storage/thr_5je2jn33zw/epic-shared-coordinator.6ohlxz/candidate.log:54` and `/Users/am/.bb/thread-storage/thr_5je2jn33zw/epic-lifecycle-fast/frontend-canary-diagnosis.log:31`.
- Healthy `/host_mnt` runtime rejected: `thr_5je2jn33zw` lines 252908–252943.
- Cold startup deadline: `thr_5je2jn33zw` lines 226913, 226945, and 232678.

Evidence: `$BB_THREAD_STORAGE/all-corpus-e2e-editor-before-query.json`, `$BB_THREAD_STORAGE/all-corpus-release-canary-backend-coupling.json`, `$BB_THREAD_STORAGE/all-corpus-release-test-fixed-port.json`, and `$BB_THREAD_STORAGE/all-corpus-recovered-summary.json`. Keep this Task in queue.
