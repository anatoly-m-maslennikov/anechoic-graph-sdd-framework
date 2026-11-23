---
atom_family: SPEC
atom_id: AN-S-2385
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Register RMED_ATOMS_BASE_REVISE discovery binding

# Summary

Register RMED_ATOMS_BASE_REVISE discovery binding

## Scope

the TOOLS capability for Tool/RMED_ATOMS_BASE_REVISE/Carrier.

## Claim

the RMED_ATOMS_BASE_REVISE discovery binding **must** be carried **in** the following TOML table **in** this Atom's Details.

## Details

```toml
[tool_binding]
name = "RMED_ATOMS_BASE_REVISE"
entrypoint = "102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/RMED_ATOMS_BASE_REVISE/rmed_atoms_base_revise.py"
action_ids = ["CA-O-105", "CA-O-106", "CA-O-111"]
workflow_ids = ["CA-O-104"]
mcp_name = "rmed_atoms_base_revise"
```

the binding registers the existing Implementation; `action_ids` identify the bounded selection, evaluation, and repair Actions that it carries. `workflow_ids` retains CA-O-104 only as workflow context, not as an Action mapping or an independent Workflow Run engine. unavailable paths **or** bindings are explicit discovery findings.
