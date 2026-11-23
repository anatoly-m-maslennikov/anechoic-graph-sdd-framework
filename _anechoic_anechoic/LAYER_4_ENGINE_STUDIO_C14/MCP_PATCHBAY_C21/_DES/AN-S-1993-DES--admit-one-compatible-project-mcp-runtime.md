---
atom_family: SPEC
atom_id: AN-S-1993
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: "active"
  version: 23
  updated_at: "2026-11-23T01:51:04.203493+00:00"
---
## Summary

admit one compatible Project MCP runtime

## Claim

### Prose Claim

Under a per-Project lock, start or reuse one healthy runtime for the selected Project and configured port. Verify its exact immutable image ID, Project mount, source fingerprint, labels, loopback binding, and readiness. Refuse a mismatch or occupied port without replacing a live runtime. Local Release owns replacement.

Fingerprint the admitted build closure, including the lock, build inputs, and stack selector. Build only when authorized. Stop before startup if inputs changed or the immutable image identity cannot be verified.

Use the verified image version and creation time for display tags. Use the selector's `test` or `beta` role during verification and `prod` after production readiness. Cache locked dependencies separately from application source. Run the installed runtime through `/opt/venv/bin/python`. Studio supervision follows AN-S-3389.
