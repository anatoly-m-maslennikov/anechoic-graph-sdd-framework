---
atom_family: SPEC
atom_id: AN-S-3467
container:
  component: C19
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: 2026-10-11 16:46:21 +0000
---
## Summary

Construct one sealed Release Version candidate manifest

# Summary

Construct one sealed Release Version candidate manifest

## Scope

Pure construction of the N/N+1 candidate inventory before release effects.

## Claim

The Tool constructs one canonical `candidateSnapshotManifest` internally by discovering current registered release definitions and their Action-to-Tool bindings, capturing current active Methodology-source Atoms at Run start, and normalizing the captured inventory into ordered repository-relative input/output rows. It binds each row to its captured bytes, digest and destination and derives one candidate manifest SHA-256 without installing, compiling, testing, deleting, or changing product or installed contents.

## Details

Construction rejects duplicate destinations, traversal, missing required Framework Methodology or Engine rows, mismatched versions, and ambiguous current selections. The same consistent snapshot is the input to every later admitted candidate phase; no Operator-supplied revision list or separate manifest refresh is required. The result is an input to later admitted effects, not a Workflow or an execution receipt.
