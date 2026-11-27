---
atom_family: SPEC
atom_id: AN-S-2519
container:
  component: C18
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver ATOM_UPDATE Tool

## Claim

This legacy route uses the scope and native exclusions in AN-S-2517.

### Prose Claim

Apply the shared connector boundary in AN-S-2478.

Use AN-S-1916 for the shared Delivery ownership and executable binding.


Use AN-S-1916 for the closed preview envelope.

Apply AN-S-2517 and AN-S-1916 to lexical validation, the profile, and its exact grammar pins. Record `subject_profile` and `subject_profile_evidence` with exactly five grammar pins and `native_admission: not_performed` in `preview_sha256`.

Validate the private transition under the distinct source and target profiles without admitting a native endpoint.


Use the preview eligibility and Carrier checks in AN-S-2517.

**Instructed Subjects-only batch binding**

Apply the instructed batch delivery in AN-S-1916.

## Details

AN-S-1916 defines shared logical operations, staged preview,
deterministic Subject intent, and direct MCP preparation.

### Batch-transition intent delivery

The ordinary schema1 Subject intent and every public preview and preparation shape in AN-S-1916 remain closed and unchanged. Only an exact active member of CA-R-866/CA-M-371/CA-O-030's explicit schema2 legacy-to-approved batch may use the following separate private intent.

The transition intent is exactly `{schema_version: 2, target, subject_profile: "approved", subject_profile_evidence, source_subject_profile: "legacy", source_subject_profile_evidence, subject_patches, proposal, execution_metadata, predecessorArchive, noop}`. The target, patches, proposal, execution metadata, predecessor archive and no-op rules retain their schema1 representations. Each profile evidence object is exactly `{grammar_pins, native_admission: "not_performed"}`; each pin is exactly `{atom_id, version, path, sha256}` with a positive Version and canonical Project-relative source path. The source pair binds the five historical legacy definitions; the target pair binds the five actual Current approved definitions. The whole object uses the existing canonical-JSON SHA-256 procedure, including both pairs and schema version. There are no optional transition fields.

Apply AN-S-2517 and the dispatch bound by AN-S-1472 and AN-S-1471.
Staging preserves the packet version and both profiles. The direct scratch
manifest remains schema1. This binding adds no singleton field, permission,
route, or runtime activation.

### Existing-Atom edit-draft staging and promotion

The existing `atom_update` Tool accepts `{operation: "stage_subject_batch", subject_batch: {path, digest}, limit?}` under CA-D-531. `limit` is a strict integer 1..10, default 10. Each call creates at most that many drafts with normal safe create-only/no-follow file checks and readback, changes no canonical/history files, and returns compact actual progress: `operation`, `state: "staging"|"staged"|"stopped"`, `count`, `completed`, `remaining`, `stage_run_id`, and `reviewed_packet: {path, digest}|null`, plus actual failure evidence. Only completed staging returns the final packet pinning every draft, preserving its schema1 or schema2 version and exact declared profiles. Preserve truthful partial artifacts; never report partial work as completed.
