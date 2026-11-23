---
atom_family: SPEC
atom_id: AN-S-3483
container:
  component: C19
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 19:05:35 +0400
---
## Summary

Verify source-pinned Candidate E2E and Full Gate aggregation

# Summary

Verify source-pinned Candidate E2E and Full Gate aggregation

## Scope

One sealed candidate fixture, its frozen N, closed Unit report, candidate image/canary, and three fixed E2E harnesses.

## Claim

The QA case **must** prove a Full Gate passes only when every declared sealed test module appears exactly once in the closed Unit or Candidate E2E phase, all three source-pinned E2E harnesses pass against the exact candidate image digest, and both reports/Journal results bind one candidate without changing N.

## Details

Exercise valid phase assignment and reject absent, duplicate, unknown, unsealed, source-digest-mismatched, or altered harness assignments; a Unit-only pass; missing candidate image/canary; tag-only or ambient image; wrong query image digest; Docker socket mount; privileged daemon option; host-path, command, image, or environment override; unallowlisted environment; non-finite/missing configured limit; inspect, harness, or cleanup timeout; stdout, stderr, or JUnit overflow; ambiguous completion; skipped, unavailable, failed, errored, duplicate, or omitted E2E case; missing, duplicate, tampered, or cross-candidate typed receipt; mismatched receipt/report candidate, image, harness path/SHA, argv, or phase digest; and incomplete aggregation. Verify the Unit executor remains closed and unchanged, E2E uses only fixed mocks/harnesses, source-pinned rows, sealed workspace, dedicated scratch, and Framework Instance configured limits, and promotion/retirement remain unavailable until the aggregate Full Gate Journal evidence passes.
