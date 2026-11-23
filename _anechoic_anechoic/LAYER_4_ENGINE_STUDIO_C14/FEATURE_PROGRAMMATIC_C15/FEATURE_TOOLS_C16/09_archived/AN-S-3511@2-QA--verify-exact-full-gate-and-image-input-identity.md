---
atom_family: SPEC
atom_id: AN-S-3511
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Verify exact Full Gate and image input identity

# Summary

Verify exact Full Gate and image input identity

## Scope

the sealed candidate gate and immutable image acceptance boundary.

## Claim

the QA case **must** accept promotion **only** when the existing Full Gate, exact image inspection and canary bind the same sealed package bytes, and **must not** accept a synthetic pass field or post-gate mutation.

## Details

The golden asserts every declared Unit module and exact three Docker E2E harnesses, manifest/catalog/version equality and immutable image digest. It changes one package byte or mode, dependency/version input, image input, test phase, receipt or canary output after sealing; each failure keeps `.anechoic_install/current.toml` unchanged. Actual Docker proof remains distinct from a test double.
