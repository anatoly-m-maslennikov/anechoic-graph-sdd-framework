---
atom_family: SPEC
atom_id: AN-S-3489
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-14 16:22:10 +0400
---
## Summary

Encode deterministic Release child manifest

# Summary

Encode deterministic Release child manifest

## Scope

The derived compiler-result manifest at one sealed Release Version child materialization root.

## Claim

Release Version **must** derive one predicted `_release_manifest.json` payload before D566 sealing, then write that exact payload only after admitted rendering at `.anechoic_anechoic/000_ANECHOIC_framework/00_APPLICABLE_METHODOLOGY/_release_materialized/<candidateSnapshotManifest.sha256>/` matches it. The payload is canonical UTF-8 JSON with sorted object keys, compact separators, `ensure_ascii=false`, and `allow_nan=false`, without a timestamp or a trailing byte. Its exact top-level members are `schema` (`anechoic.release_version.child_materialization.v1`), `candidate_release`, `compiler_entrypoint_path`, `compiler_entrypoint_sha256`, `canonical_source_snapshot_digest`, `compiler_frontier_digest`, `actual_derived_source_copy_sha256`, `nested_source_recursive_sha256_before`, `nested_source_recursive_sha256_after`, and `output_rows`. `output_rows` contains every emitted projected output file other than `_release_manifest.json` itself, each with exactly safe child-relative `path` and lowercase 64-hex `sha256`, sorted ascending by `path`.

## Details

The pure preflight uses the current canonical source bytes and existing `compile_report` plus `projection_bytes` in memory only. It derives the expected projected bytes, their `output_rows`, the canonical payload, and the complete predicted child-tree digest before D566 sealing; it performs no copy, staging, replacement, Journal append, or runtime effect. For this calculation it uses a fixed safe one-component candidate child placeholder and proves that replacing that placeholder with the actual 64-hex candidate manifest component leaves every projected byte unchanged, because existing projection provenance depends on the source-relative path depth rather than that component's value. Preflight fills the payload's `actual_derived_source_copy_sha256` from the sealed expected derived-copy equality target as predicted data; it is not a claim that delivery has occurred.

After the derived copy is actually admitted, the renderer recomputes the same bytes from the current bound inputs, requires the observed derived-copy digest to equal the sealed expectation, and requires every projected byte, the canonical child-manifest bytes, and the complete child-tree digest to equal the preflight predictions before emitting `CompilerSuccessEvidence` or `SealedCandidateCompilation`. At that point `compiler_entrypoint_*` identifies the executing compiler bytes; canonical and frontier digests bind the current source facts; the derived-copy digest is observed; and the nested-source values must compare equal before and after materialization. Paths remain child-relative, unique, safe, and exclude the manifest's own path.

The child manifest contains neither a self `sha256`, any final or expected compiled-tree digest, nor `candidateSnapshotManifest.sha256`. Including its own digest or an output-row digest for itself would create a self cycle; including the final compiled-tree digest or candidate manifest identity would create a cross-hash cycle through D566's expected compiled output. The child-tree digest remains an external, locally observed D567 handoff value after the complete child exists. This derived result does not revise canonical authority, mutate the canonical projection, or authorize packaging, installation, promotion, retirement, Journal recording, or a C447 relocation bypass.
