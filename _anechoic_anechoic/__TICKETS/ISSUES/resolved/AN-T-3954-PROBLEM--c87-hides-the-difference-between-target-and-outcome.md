---
atom_family: TKT
atom_id: AN-T-3954
concern:
- subject: C87
  path: Project Structure.components
  relation: affects
container:
  component: C87
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C87 hides the difference between target and outcome

## Claim

### Prose Claim

A terminal target and a terminal outcome produced identical diagrams. Lean changed its verdict from matched to unresolved between the two fixtures.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_3_MERMAID_RENDERER_C87/workflow_diagram__pub.py:14.

## Resolution criteria

Label target and outcome independently in Mermaid.

## Resolution

The Mermaid regression distinguishes target from outcome and preserves the distinction between null and text.
