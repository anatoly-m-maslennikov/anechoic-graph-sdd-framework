---
atom_family: TKT
atom_id: AN-T-1945
structure:
  container:
    component: C15
  priority: 2
context:
  template: problem
state:
  status: resolved
  version: 3
  updated_at: '2026-10-21T12:09:01Z'
---
# Summary

Prevent Docker test network address-pool exhaustion

## Concern

The actual Local-release suite cannot create required disposable Compose networks because Docker reports all predefined address pools fully subnetted. Determine positively attributable unused test resources and the canonical cleanup-lifetime gap before repairing or retrying. Do not infer permission to prune all networks or alter Docker daemon address-pool settings.

## Evidences

Run local-20261021-isolated-gate-114321 log .anechoic_tmp/simple_local_release/local-20261021-isolated-gate-114321-tests-n4u1m0et.log records test_docker_e2e.py anonymousHTTPstartup RuntimeError during networks anechoic-d7866cf7f7c2_http_publication/runtime creation. Module3tests/1error135.597s; crash-publication25tests passed397.444s. Root intentionally interrupted exactownedreleasePID96380 after failedgate; terminalreportfailed/tests/KeyboardInterrupt is not the underlying Docker failure. Prior release attempts also used disposable Compose Projects; stale-network ownership and exact origin remain unproven until inspection.

## Blast radius

Isolated test infrastructure and ability to complete the full Local-release gate. No evidence of production MCP failure; preserve working MCP, foreign/unknown/referenced networks, volumes and installedimage. Release remains uninstalled. Root owns exact validated cleanup only; no broadprune, force, inferredownership or unrelated daemon reconfiguration.

### Actual result and next boundary

The Operator explicitly approved deleting the exact 25 empty networks despite unrecoverable Project ownership. Root verified full ID/name/Compose labels, zero endpoints and absence of references from every container immediately before each non-force removal. All 25 IDs are absent; no other unknown network was selected. Separately, two exact failed-attempt containers, their one network and uniquely labelled unused test image were cleaned after release processes exited; volumes and host evidence retained. Production e812/08f/network6e489 remain healthy unchanged; five networks now remain. Existing ordinary test teardown already calls scoped down; no current normal-path leak is proven. C567 records unproven failed-start/forced-interruption edge cases. P2541 validates recovery before fresh full release.

### Recovery verification

After approved bounded cleanup, the actual previously affected Docker module passed3/3 with zero skips94.378s; module96.201s. Its exact five-network baseline and original production container/image/network are unchanged after fixture teardown, and canonical owner removed its unused test image. The observed capacity blocker is resolved without daemon settings, production code changes or broad cleanup. C567 remains a separate unproven failed-start/forced-interruption risk. This is focused recovery acceptance, not a full release success.
