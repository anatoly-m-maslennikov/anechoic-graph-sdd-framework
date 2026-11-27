---
atom_family: SPEC
atom_id: AN-S-5172
container:
  component: C61
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.217949+00:00'
---

## Summary

Audit Realization Graph Packages and exact Spec Bindings

## Claim

Publish `package_audit` with one row for each local Package node, including Test Packages and Packages without a Spec.

- Report each current entry marker defined by AN-S-4837. Report older `__pub` markers as legacy observations.
- Report `missing_visibility_marker` when a tested Package lacks a current entry marker.
- Report `missing_test_target` on a Test Package whose parent qualifies as neither Package nor Component.
- Report canonical `__spec_bind.yaml` presence and whether the binding is missing, invalid, empty, or valid. Use the full Package folder name for the sidecar.
- Check every `implements` and `applies` pin against the exact active Spec revision. Resolve legacy pins only through an unambiguous exact alias.
- Report each failed pin and its reason. Distinguish archived, missing, ambiguous, and non-Spec references. Leave the active-pin result unknown if there are no valid pins.
- For a Component Seed, report its active Component Seed Manifest reference and whether `implements` pins that exact revision. Leave Contract coverage unknown when the Component Seed Manifest or ownership cannot be established.
- Report an invalid Component Seed Manifest or unreadable ownership to stderr. Keep the other Package audit facts available.
- Contract coverage records a trace to the Component Seed Manifest. Evidence from implementation and tests establishes Contract satisfaction.
- Refresh on admitted source, sidecar, and Spec changes. Publish in the same DuckDB transaction as the changed projection and rebuild with its dependencies.
