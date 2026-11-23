---
atom_family: PROJECT_CONFIG
atom_id: AN-P-49
structure:
  container:
    component: C27
context:
  template: workflow
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-22T00:02:04.989467+00:00"
---

## Summary

Prepare public release drafts

## Claim

### Formal Claim

```python
release_command(
    operation="public",
    entrypoint="LAYER_5_FRAMEWORK_DELIVERY/release.py",
)
```

### Semantics

When the Project Manifest enables release Workflows, MCP reads this Active
Project Config Claim and returns the host `uv` command for the selected
Project and run ID. The Operator runs it on the host. MCP performs no
release effects.

## Operation

Public Release prepares a detailed Pull Request description and a brief Version History entry for the selected Git comparison.

Resolve the base and head to immutable commits and read the selected Version from the pinned head. Read completed Task and Epic content directly from Git. Delegate a Luna review of the pinned diff against those tickets to identify missed changes. Render both drafts from reviewed content bound to the same commits.

The result is draft text for the Operator. This Workflow does not change repository files, commit, push, create or update a Pull Request, run a public suite, or use Journal. A failed or mismatched comparison stops without a draft.
