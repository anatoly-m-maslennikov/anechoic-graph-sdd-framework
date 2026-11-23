---
atom_family: TKT
atom_id: AN-T-566
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 08:10:13 +0400
---
## Summary

Build Release Version contract golden tests

# Summary

Build Release Version contract golden tests

## Objective

Within <=15 minutes, build Release Version contract golden tests.

## Details

Own new RELEASE_VERSION/tests/test_release_contract.py and explicit mocks only: e2e-style request-to-result pure preparation checks, missing/forged/unsealed/currentness/digest/path errors and good complete Framework manifest. Follow R1876–1880/M331–333/E571–574/D560–564 exactly; coordinate API with P1639. No effects or mocked promotion presented as actual proof.

Inputs are P1622 accepted source/RMED pins: O164–179@1, R1876–1880@1, M331–333@1, E571–574@1, D560–564@1. D561/E572 are the repaired accepted pins, not their rejected predecessors. Preserve external dirt and designated C447/C449 boundaries; existing development worker tests are not fresh-image proof.

## Definition of Done

Save exact bounded output and test/remaining-coverage evidence. Pure preparation, staging or source review never establishes release promotion, complete P1623, P1624 or Epic closure.

## Result

Current test_release_contract.py SHA-256 edc319999c1cfffeba862d46c7d5219e47536124b7b2fd3e5822ad5801326db1 supplies fourteen strict candidate-encoding cases; P1657 supplies thirteen additional locally observed handoff golden cases. All 27 passed in the existing development worker after the raw-mapping prototype repair. Positive compiler handoff fixtures are explicitly mocked and are not actual compiler or release proof. The corpus preserves refusal/currentness/path and zero-effect boundaries.
