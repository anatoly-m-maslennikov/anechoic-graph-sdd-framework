---
atom_family: SPEC
atom_id: AN-S-1471
container:
  component: C16
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 5
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---
## Summary

Deliver sealed lifecycle dispatch interface

## Claim

### Prose Claim

AN-S-1472 defines the shared sealed lifecycle dispatch interface. Apply
these additional requirements to the explicitly admitted legacy-to-approved
batch.

## Details

### Explicit batch-transition packet

The existing closed schema1 packet and singleton request in AN-S-1472 remain unchanged and reject `source_subject_profile`. A separately instructed legacy-to-approved batch uses exactly `{schema_version: 2, subject_profile: "approved", source_subject_profile: "legacy", git_checkpoint, atoms}`. The source-profile field is required in schema2; missing, null, empty, unknown and every other value are rejected. Keep the same complete target, ordered patch and optional draft descriptors; all members have draft pins or none do. Both map-only and draft-backed schema2 batches retain the existing ordered effects, checkpoint, authorization and first-failure rules. The outer request is still exactly `{subject_batch: {path, digest}}`.

Only the dispatcher for the exact active pinned schema2 member may pass `source_subject_profile: "legacy"` in its private per-member preparation/effect request alongside the approved target profile. Bind that private request to the same packet digest, target and ordered patches. Outside that exact active batch, the ordinary public singleton, preview and direct preparation contracts reject the field. No caller field or matching text alone creates batch admission.

Use the closed intent in AN-S-2519 and the transition rule in AN-S-2517.
Preserve the authorization, effects, readback, and restoration obligations
of the dispatch interface in AN-S-1472. This binding adds no approval round,
source effect, or runtime activation.
