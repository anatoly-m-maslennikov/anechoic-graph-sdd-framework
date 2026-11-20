---
identity:
  atom_id: AN-S-1375
context:
  container:
    component: C46
  tier: 5
  lens: QA
state:
  status: active
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify the shared View rename modal

## Claim

### Prose Claim

Use the built Workbench and real Workspace backend. Double-click current View name or choose Rename View from palette: the same shared modal opens with current displayed name prefilled. Confirm updates current View and existing persistence/local state through refresh/reload; Cancel/Escape leaves name unchanged. Single click and unrelated query/autosave controls introduce neither click-only rename nor separate workflow. Prefer visible browser E2E and existing rename API, not private Svelte state.
