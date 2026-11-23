---
atom_family: SPEC
atom_id: AN-S-3509
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

Verify bootstrap, adoption, multi-project and relocation contexts

# Summary

Verify bootstrap, adoption, multi-project and relocation contexts

## Scope

the target-context fixture matrix.

## Claim

the QA case **must** verify distinct bound contexts for bootstrap, metadata adoption, non-git, two-Project repository and relocation cases, and **must not** accept inferred target controls.

## Details

Each positive fixture reopens root/control child, settings, Structure and registry digests. Adoption succeeds only with an empty runtime boundary; non-git uses false repository identity; siblings have different context/locks; relocation links prior context without retaining old absolute root as identity. Missing, ambiguous, changed or active-runtime inputs refuse without state writes.
