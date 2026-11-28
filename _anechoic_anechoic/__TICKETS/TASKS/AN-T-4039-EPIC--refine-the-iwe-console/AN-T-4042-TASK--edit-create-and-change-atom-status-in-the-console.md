---
atom_family: TKT
atom_id: AN-T-4042
container:
  atom: AN-T-4039
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T22:18:31Z"
---
## Summary

Edit, create, and change Atom status in the Console

## Work

Add Edit to the full Document view. For a Current revision, reopen its
existing Draft or create a Draft through the lifecycle tool and open
it in the editor. Save changed input every five seconds through the
lifecycle tools. Add a Create Atom button that uses the same tools.

Provide quick × controls for removable entries such as authored
relations in the Draft. Use the same autosave flow for these changes.
Show buttons for the status changes allowed for the displayed Atom.
Selecting Active on a Draft promotes it through the lifecycle tool.

## Acceptance

Verify Draft creation, reuse, five-second autosave, and a relation
removal. Verify Atom creation and an allowed status change. Confirm
that selecting Active promotes the edited Draft and that its updated
content appears as Current.

## Verification

All 13 lifecycle browser cases passed. Three generated cases cover
navigation during a pending save. Navigation waits for the newer edit
to save. Refusal of either save retains the newer edit in the editor.
Lean matched all 17 captured fields for these cases.
See AN-S-3060@17 and AN-S-3372@10.
