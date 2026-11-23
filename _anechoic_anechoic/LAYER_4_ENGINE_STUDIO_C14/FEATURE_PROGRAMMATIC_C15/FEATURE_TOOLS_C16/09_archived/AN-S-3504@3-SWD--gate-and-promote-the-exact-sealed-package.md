---
atom_family: SPEC
atom_id: AN-S-3504
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Gate and promote the exact sealed package

# Summary

Gate and promote the exact sealed package

## Scope

the candidate Full Gate, image proof and no-substitution promotion procedure.

## Claim

the INSTALL_TOOLS facade **must** run and reopen the existing Full Gate and immutable image proof on the same sealed package bytes **before** promotion, and **must not** promote a reconstructed or Boolean-approved package.

## Details

1. Require the closed Unit Gate evidence for the compiled candidate, then freeze candidate package manifest, catalog and version rows under the candidate root.
2. Build, immutable-ID inspect and canary the exact sealed tree; reopen immutable image, package, catalog and version bindings.
3. Run the exact three host-capable Candidate E2E harnesses against that immutable image, then aggregate Unit Gate, build, canary and E2E evidence into the existing Full Gate.
4. Copy or atomically move the unchanged gated tree to its digest release root; only then atomically publish `.anechoic_install/current.toml` under the installation lock. No package or image is rebuilt after gate aggregation.

Any changed row, receipt, image or promotion destination blocks and preserves evidence.
