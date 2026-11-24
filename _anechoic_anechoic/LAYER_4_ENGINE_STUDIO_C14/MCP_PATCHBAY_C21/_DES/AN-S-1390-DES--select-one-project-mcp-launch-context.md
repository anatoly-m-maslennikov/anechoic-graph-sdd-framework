---
atom_family: SPEC
atom_id: AN-S-1390
container:
  component: C21
tier: 3
context:
  lens: DES
state:
  status: active
  version: 19
  updated_at: "2026-11-23T01:48:06.179432+00:00"
---
## Summary

select one Project MCP launch context

## Claim

### Prose Claim

The Project MCP launcher must resolve one safe explicit Project context or refuse without selecting or affecting another Project. Validate the canonical Project root and selected control root; reject traversal, symlink substitution, missing, invalid or ambiguous local controls. Do not search parent directories or Git ancestors. A locally valid explicitly selected nested Project is allowed.

Carry the host root, control root, and container mapping through startup. Compute the Project instance ID from the SHA-256 of the canonical host root, NUL, and control-root-relative path. Keep per-Project state and locks isolated; do not reuse or clean another Project's state. The launcher may read the Project Manifest and runtime settings through declared interfaces.

In single-Project mode, a supplied `project_root` assertion must match the binding. Shared calls require an explicit Project. Reject invalid or mismatched assertions before execution and keep routing context separate from native Tool arguments. Initialization and discovery are protocol operations, not Tool-call envelopes.
