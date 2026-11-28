---
atom_family: TKT
atom_id: AN-T-4092
container:
  atom: AN-T-4087
priority: 2
context:
  template: task
  label: Task
relations:
  IS_BLOCKED_BY:
  - AN-T-4088
  - AN-T-4089
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T08:08:02+00:00'
---
## Summary

Seal and qualify the exact v0.5.0 candidate

## Work

Seal the agreed amm/dev source in a clean disposable checkout with
version.toml set to 0.5.0. Record the immutable source SHA, public base
SHA, Model and Manifest pins, and built image ID.

## Acceptance

Use the supported Release commands and the full suite. Record passing
Static, required host Functional, packaged image tests, the real MCP
canary, and installed runtime verification. Bind the receipts to the
same source and image.

Complete the code and test conformance review in AN-T-4089 before
release. Bind both results to the sealed source.

If a fix changes the candidate, verify the new inputs through the
supported release continuation.

## Source preparation

The Godot Favicon project now uses regular files with byte-identical
script and shader contents. The supported `prepare-local` command
sealed qualification probe `c406b2b40a32d0e89f713274e0b415519e45bb06`
with isolated Project settings. Requalify the final source after the
Formal Spec review and remaining Functional fixes.

The preceding `28d67aacfaeebb5552590de5de659167b78c3b8f` seal ran
1,032 host Functional tests across 159 modules. Twelve modules failed.
The two reuse receipt tests pass with their corrected expectations on
the probe. The remaining failures include startup waits and a
manifest-only edit that fell back to a full rebuild. Diagnose those
failures before running the final gate.

The manifest-only failure reproduced on the qualification probe. Managed
Worker startup supplies an ingested Model source and disables the compile
path required for `compiler_refresh`. Keep Model admission and the schema
change fallback when correcting this dispatch.

The correction passes the C91 process test. It uses `compiler_refresh`
for the Manifest-only edit and rebuilds after a schema change. Include
the Worker changes and their targeted tests in the next seal.

The isolated sequential rerun passed all 38 selected startup, database,
watcher, and Archive tests. The host run allowed `ps` for the Archive
test. The full Functional gate remains open for the final source.

Probe `b597aa0eac2d50cf01b93d6c126f14e384556fb4` includes the
Worker and Console corrections and the four proposed Active Formal
Spec pairs. The isolated source qualifies the proposed bindings before
promotion in the shared checkout. It passed preflight and the exact
C91 process test for Manifest refresh and schema-change rebuild.

Its Static gate stopped on a test helper format change, two oversized
test functions, and two denied test imports. Image verification did
not start. The next seal repairs those tests within the current
Code Access rules. Probe `380b9885dc637b72cfae0c8bc41eb85b1f8b231d`
passed preflight and all 53 Static tests. It entered the supported
`verify-image` command on its isolated Project. Full Functional and
installed runtime verification remain open.

Probe `0bcec465e0c153575d1e3d6b39482aef1d59e908` includes the C30
pins, C21 case driver and wire assertions, and Console heading fix.
Preflight and all 53 Static tests passed. The host Functional run
stopped after a required Autoform comparison skipped. Use the pinned
Autoform, Joern, and Lean paths for the next full run.

Probe `ce8841c1a4b30ca61484049229e1f53444e7b210` also includes the
publisher fix. It passed preflight and all 53 Static tests. The full
Functional run uses the pinned formal tools, with one ordinary host
worker. Image verification follows a passing host gate.

The first Functional failure on this probe was the historical saved
query fixture. The shallow checkout lacked its pinned revision.
The checkout now reads the required Git objects from the local object
store, and its sealed source is unchanged. The remaining modules still
run to identify independent failures. The exact failed historical test
passed on replay from the repository root with the pinned revision.

`prepare-local` now retains base history with an isolated port.
All seven preparation tests passed, including a CLI check that reads
a file from the base's ancestor. The next qualification run must use
a source with the complete required history.

Seal `390073d598be9bb0e70832c483d12d506f075210` has that history.
It passed all 53 Static tests with pinned Lean, and the exact historical
fixture passed without a Git object link from another checkout.

Qualification seal `a99d4b4950386032405d5e7ab00a753842bf1f66`
adds three Active Spec sidecars and the legacy Setup migration step.
Preflight and all 53 Static tests passed with pinned Lean. In the full
Functional run, all five historical regressions passed. The remaining
Functional checks precede image verification on OrbStack.
The exact Realization Graph found zero blocking imports and zero
production imports from Test Packages. It records 26 advisory sites.

The `a99d4b49` Functional gate found 18 lifecycle matrix failures.
The grid now uses the bound Model fixture for Project SPEC validation.
All 1,642 cases and the seven companion tests passed in the checkout.
The required Functional gate must run against the corrected seal.

The launcher concurrency case reproduced a first-use state directory
race. With the directory fix and one resolver patch across both threads,
all 27 focused launcher tests passed. The shared routing case separately
hit the 15-second Model attestation timeout. It passed in isolation with
the production deadline. Two concurrent attestation probes finished
within 1.6 seconds each.

The original gate ran 1,034 tests in 159 modules and reported three
failed modules. Seal `cd3c911537d0213b33172713a2b66cdac4d68cf4`
contains only the lifecycle fixture and launcher fixes. The new full
qualification run keeps the production deadline.
Preflight and all 53 Static tests passed. Full Functional is running.
The corrected Realization Graph reports zero blocking imports and zero
production imports from Test Packages. The 26 advisory sites remain.

The corrected host run missed the managed-build test's 10-second warm
Worker socket wait. A direct probe on the same seal published its socket
in 1.532 seconds and stayed alive. The failing integration case still
needs replay with the full host run out of the way.

The committed `amm/dev` merge replay with `ce8841c1` had no conflicts.
Its tree adds only the AN-T-4099 planning Ticket to the seal. The
working checkout also contains concurrent edits. Review their scope
before freezing the final source and retain the matching receipts.
