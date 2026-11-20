---
atom_family: TKT
atom_id: AN-T-591
structure:
  container:
    atom: AN-T-592
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Implement accepted reversal evidence pins

## Objective

Within <=15 minutes after P1571 source ACCEPT, complete the existing safe native provider's exact evidence-currentness bindings.

## Details

- Dispatch remains blocked until P1571 accepts exact current D536 source bytes. Read accepted D536/R1833/E553/E554 and P1568's safe fail-closed result first.
- Own native_revert_provider.py, a narrow evidence reader if necessary, and directly affected native-provider/selected-provider focused tests only. Preserve the safe permission/path/budget/JSON/Event checks already implemented. No source, shared executor/backend, fixture, MCP, Plan, Journal or commit writes.
- Consume exactly the accepted current pin schema for governing-definition identity/revision, actual recorded Operator decision and executor permission, selected-change/history/before-after and affected references. Reobserve actual source/evidence at admission, pre-execution and before every effect. No fabricated authority, arbitrary resolver, duplicate Journal or inverse inference.
- Functional tests use real disposable current records and canonical Event evidence where declared. Prove current exact native reversal succeeds and post-admission revocation/change blocks before Action start or remaining effects. Coordinate the accepted fixture interface with P1567; use deterministic existing structural recovery for W10 if needed, not forecasted timestamp-dependent hashes.
- Inherit 90%; use apply_patch and preserve concurrent edits. No FPF, harvesting, paid Agent, permission bypass or live Project mutation. Root saves and records separate native/transport/image proof.

## Saved result

All accepted evidence pins now reobserve actual source/evidence at admission, pre-start and each effect. Exact recorded decision includes full ordered effects; same IDs with changed parameters are denied. Current combined Revert suites passed 24/24 and exact registered selected Revert case passed. Independent P1581 ACCEPT. Provider hash fcf61f100eb8fd194d3c066f23c82c5825249a3cbf9d5e0f849d5bbe975ace45. Two unrelated W09 startup tests are blocked by concurrently stale prompt bindings; no all-image claim.

## Definition of Done

Accepted evidence pins are implemented with passing bounded current/changed/revoked functional proof; native happy-path/image closure are never inferred from synthetic references.
