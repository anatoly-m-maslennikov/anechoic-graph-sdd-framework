---
atom_family: SPEC
atom_id: AN-S-3360
concern:
  subject: "Module/(.Language := python)"
  path: "Model/Graph/Node//Artifact//SSOT//Realization/Content"
  relation: "is_contained_by"
container:
  component: C14
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 6
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Precompile Studio Python imports

## Claim

### Prose Claim

Precompile installed Studio Python Modules and dependencies once for the target interpreter and final installed paths. Use the source bytes imported by the staged runtime. Apply this to Studio entry points and child processes in `dev`, `test`, and `prod`.

Use the Python cache boundary in AN-S-1342 and disable runtime bytecode writes. Rebuild the cache when the interpreter or source changes. Validate a cache that can outlive its source installation with a source hash. Exclude mounted Project sources from the installed cache build. Verify staged imports with bytecode writes disabled.

Use the locked Engine environment for Studio. Use separate locked Release and Setup environments for their own entry points. Include profilers only in diagnostic test images, not in a candidate eligible for production. Verify the exact candidate's source and dependency inventory before promotion.
