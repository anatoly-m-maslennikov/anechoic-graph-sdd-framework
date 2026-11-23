---
atom_family: SPEC
atom_id: AN-S-1103
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 8
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Keep one commit-automation manager pure and deterministic

# Keep one commit-automation manager pure and deterministic

## Claim checked

the commit-automation manager owns **all** decisions **without** performing I/O.

## Test case

supply equal typed queue, repository, action, result, settings, lease, circuit, **and** clock facts twice while replacing filesystem, subprocess, environment, network, persistence, **and** logging adapters with fail-on-call sentinels.

## Acceptance criteria

both calls return byte-equivalent typed plans **or** commands; no sentinel is called; **every** target, ordering, acceptance, fallback, retry, **and** terminal decision appears **in** the result.

## Failure disposition

reject the manager on the first effect, hidden input, nondeterministic result, **or** unowned decision.
