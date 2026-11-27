---
atom_family: SPEC
atom_id: AN-S-1993
container:
  component: C21
tier: 3
context:
  lens: DevOps
state:
  status: "active"
  version: 26
  updated_at: "2026-11-27T18:48:35.403216+00:00"
---
## Summary

admit one compatible Project MCP runtime

## Claim

### Prose Claim

Under a per-Project lock, start or reuse one healthy runtime for the selected Project and configured port. Verify its exact immutable image ID, Project mount, source fingerprint, labels, loopback binding, and readiness. Refuse a mismatch or occupied port without replacing a live runtime. Local Release owns replacement.

Require `stack = "current"` in the Release configuration. Fingerprint the
admitted build closure, including the lock and build inputs. Build only
when authorized. Stop before startup if inputs changed or the immutable
image identity cannot be verified.

Use the verified image version and creation time for display tags. Use the
`test` display role during verification and `prod` after production
readiness. Cache locked dependencies separately from application source.
Run the installed runtime through `/opt/venv/bin/python`.
