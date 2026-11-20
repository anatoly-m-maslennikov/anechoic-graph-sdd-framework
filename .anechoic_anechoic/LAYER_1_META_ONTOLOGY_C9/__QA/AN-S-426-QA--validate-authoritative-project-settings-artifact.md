---
atom_family: SPEC
atom_id: AN-S-426
structure:
  container:
    component: C9
  tier: 8
context:
  lens: QA
state:
  status: active
  version: 41
  updated_at: '2026-11-20T11:29:16.610639+00:00'
---

## Summary

Validate Authoritative Project Settings Artifact

## Claim

Reject a Project Manifest as authoritative when it violates its registered placement, uniqueness, content boundary, applicable schema or field specifications, or treats another Atom, an unadmitted Carrier or a Projection as an independent source of selected Project values. For history binding, require an exact current Revision, SHA-256 Digest and admitted Work Journal receipt.

## Details

An ordinary Manifest read validates the complete actual Carrier and returns immutable values with the exact selected Project, physical path, raw SHA-256 Digest and declared schema marker. It does not query the Work Journal or determine logical Revision or currentness; history binding and recovered baseline registration are separate operations. Neither reading nor refusal authorizes writes, fallback or migration.

For recovered baseline registration, check the selected Project, Carrier path, lineage-derived logical Revision and Digest binding, unchanged Carrier bytes, actual observation time and evidence-backed observing Run or session. Reject absent or ambiguous binding, stale Digest, path-based Revision reset, guessed allocation or fabricated change, author or history. An admitted receipt does not replace schema or ownership checks or authorize another operation.
