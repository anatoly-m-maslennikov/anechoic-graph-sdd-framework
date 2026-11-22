---
atom_family: SPEC
atom_id: AN-S-2386
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 15
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Register VALIDATE_ATOMS discovery binding

## Scope

the TOOLS capability for Tool/VALIDATE_ATOMS/Carrier.

## Claim

### Prose Claim

the VALIDATE_ATOMS discovery binding **must** be carried **in** the following TOML table **in** this Atom's Details.

## Details

```toml
[tool_binding]
name = "VALIDATE_ATOMS"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms.py"
action_ids = ["CA-O-087"]
workflow_ids = []
mcp_name = ""
```

the binding registers the existing Implementation; it does **not** claim an independent Action **or** Workflow Run engine. unavailable paths **or** bindings are explicit discovery findings.
