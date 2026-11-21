---
atom_family: SPEC
atom_id: AN-S-1303
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reproduce a locked uv environment

## Claim

### Prose Claim

From an empty environment, `uv sync --locked` then declared `uv run --locked` must use the selected Python boundary and Method-selected dependencies without changing `pyproject.toml` or `uv.lock`; stale lock, implicit resolution or unauthorized dependency rejects reproducibility.
