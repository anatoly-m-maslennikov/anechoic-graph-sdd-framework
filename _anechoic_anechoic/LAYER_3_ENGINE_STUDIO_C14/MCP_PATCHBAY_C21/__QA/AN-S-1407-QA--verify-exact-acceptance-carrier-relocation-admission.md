---
atom_family: SPEC
atom_id: AN-S-1407
structure:
  container:
    component: C21
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 14
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify exact acceptance-carrier relocation admission

## Claim

### Prose Claim

the exact acceptance-carrier relocation admission **must** pass its declared unchanged-bytes and no-broadened-authority checks.

## Details

### Relocation admission checks

- Exactly one candidate replaces exactly the three registered prior source paths with their registered current paths; carrier bytes, identities, versions, and digests remain unchanged.
- Malformed, duplicate, missing, unknown, unsafe, stale, or mismatched registration fields, input hashes, or path occurrences refuse before effects.
- Routes, graph edges, registry identity, source digests, and fixed-path refresh behavior remain unchanged. Only the three registered path occurrences, canonical serialization, and derived canonical_manifest_sha256 may differ; route-identical selected_binding_digest remains unchanged. Aliases, raw-manifest edits, and general relocation requests refuse.
- Publication uses trusted Operator context, lock, pending intent, exact readback, and a real Work Journal receipt. An interrupted pre-effect attempt may retry the same candidate once only when exact original input, sealed intent, and current sources match; once it exists recovery is recording-only without rewrite. Ambiguous bytes refuse.
