---
atom_family: SPEC
atom_id: AN-S-463
container:
  component: C15
tier: 6
context:
  lens: DEVOPS
state:
  status: "archived"
  version: 28
  updated_at: "2026-11-27T14:45:10.285943+00:00"
---

## Summary

Bind Project Settings Revisions to Journal Receipts

## Claim

The current Project Manifest Revision and SHA-256 Digest bind to its exact authoritative Carrier through a canonical completed governed-change Work Journal receipt or an explicitly authorized canonical recovered-state receipt. The receipt matches the selected Project, exact Carrier path, logical Artifact Revision and Digest; absence, ambiguity or mismatch leaves currentness unknown.

## Details

Recovered baseline registration uses the existing `recovered` event for `governed_project_state`, with the positive-integer logical Revision in `result.version` and `path`, `sha256`, `observed_at` and `observer_run_id` in `recovery_evidence.carrier`. Observation time is actual and the observing Run or session is supported by evidence; unresolved history remains uncertain. Revision follows the Artifact lineage across Carrier moves or renames and is not reset or guessed from a path. Registration does not change Manifest bytes, fabricate a past change or author, or rewrite Journal history. A changed Carrier is not presented as the registered current baseline. Registration proves the observed binding, not schema conformance or authorization or correct performance of another operation.
