---
atom_family: SPEC
atom_id: AN-S-3498
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Promote only a sealed package with exact gate and image proof

# Summary

Promote only a sealed package with exact gate and image proof

## Scope

the private candidate-to-reusable-package promotion boundary.

## Claim

the INSTALL_TOOLS facade **must** promote **only** a candidate sealed beneath `.anechoic_tmp/release_candidates/<run_id>/` after the existing Full Gate and image proof reopen against its identical package bytes.

## Details

The candidate seal, Full Gate receipt, immutable image inspection and canary all carry the same package manifest SHA-256, source catalog digest and sealed version carrier. Promotion verifies unchanged ordered rows and modes at the destination and then may update the sole `.anechoic_install/current.toml`. Failed or uncertain proof retains candidate evidence and leaves current selection unchanged.
