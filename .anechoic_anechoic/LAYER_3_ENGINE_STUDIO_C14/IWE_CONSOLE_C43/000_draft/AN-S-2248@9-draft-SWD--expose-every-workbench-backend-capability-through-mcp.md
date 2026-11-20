---
atom_family: SPEC
atom_id: AN-S-2248
structure:
  container:
    component: C43
  tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 9
  updated_at: '2026-11-14T07:53:07.557473+00:00'
---
## Summary

Expose every Workbench backend capability through MCP

## Claim

### Prose Claim

Implement Workbench backend capabilities once. Web and MCP expose the same
arguments, results, errors, saved URLs, and shared Workspace and View state.

## Details

- Browser preferences and local drafts stay in the browser.
- Use Run with Save for Bookmarks and View Save for saved Views.
- Share result delivery and explicit SQL reads across both adapters.
- Native Codex chat owns conversation control.
