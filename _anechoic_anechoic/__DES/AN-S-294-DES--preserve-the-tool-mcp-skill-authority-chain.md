---
atom_family: SPEC
atom_id: AN-S-294
structure:
  container:
    component: C00
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-10-27 19:59:55 +0400
---
## Summary

Preserve the Tool-MCP-Skill authority chain

# Preserve the Tool-MCP-Skill authority chain

the FPF Extension **must** realize deterministic behavior first **in** canonical project-local Tools, expose admitted Tool contracts through the project-local provider-neutral MCP service **without** changing their meaning, **and** make the `fpf` Skill a thin direct consumer of that MCP surface; the Skill **must not** duplicate Tool mechanics, MCP transport, lifecycle control, **or** a `ca` routing wrapper, **and** Consumer-owned Demands **must not** be admitted **before** they target **`=1`** identified current MCP Implementation result.
