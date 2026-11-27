---
atom_family: SPEC
atom_id: AN-S-1375
container:
  component: C46
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Verify the shared View rename modal

## Claim

### Prose Claim

Exercise the built Workbench with the real Workspace backend. A double-click on the current View name opens the existing shared rename modal with the currently displayed name prefilled; the Operator can edit and confirm the name through the existing rename contract.

| Case | Expected result |
| --- | --- |
| Double-click the current View name | The shared rename modal opens with that View's current name, not an empty value. |
| Edit the prefilled name and confirm | The current View shows the new name and the existing Workspace persistence/local browser state retain it after refresh or reload. |
| Cancel or press Escape | The modal closes and the View name remains unchanged. |
| Open Rename View from the command palette | The same shared prefilled modal and confirm/cancel behavior are used. |
| Click the View name once or use unrelated query/autosave controls | No new click-only rename button or separate rename workflow is introduced. |

Prefer browser end-to-end checks with visible controls and the existing rename API; do not inspect private Svelte state.
