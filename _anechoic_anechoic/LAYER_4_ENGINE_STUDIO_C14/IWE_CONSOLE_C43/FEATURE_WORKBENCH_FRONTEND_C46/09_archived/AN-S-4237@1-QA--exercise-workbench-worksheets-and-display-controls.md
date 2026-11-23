---
atom_family: SPEC
atom_id: AN-S-4237
container:
  component: C46
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-04 23:19:17 +0400
---

## Summary

Exercise Workbench worksheets and display controls

## Claim

### Prose Claim

The Workbench interface preserves Worksheet input and uses the shared backend contracts for its query and saved-resource actions. Exercise the accepted controls through the built frontend and focused component or state checks.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Light, Dark and System | Each mode is selectable; the choice is remembered; focus and result text remain readable. |
| Text zoom | Editor, buttons, tabs, menus, headings, result and status text change size. Layout dimensions and icons are not multiplied. |
| Two Worksheets | Inputs and displayed results stay with their own tabs. Closing unsaved input asks first. |
| Five-second autosave and reload | Whole scripts and open-tab state restore without clicking Save. Browser unload flushing is best effort; storage failures are visible and are not false success. |
| Native window close warning | Unsaved input uses the browser warning when the browser permits it; no cross-browser controller is added. |
| Collapsed editor | The spoiler expands the same input and preserves its cursor while the page remains open. |
| Completion | Actual tables and columns are offered, including quoted dotted/spaced content columns; the editor does not execute SQL for suggestions. |
| Cursor actions | Run and Cmd+Enter execute the current statement; Check and Shift+Cmd+Enter check it; Save saves it; Save Worksheet saves the entire script. |
| Saved resource links | Show ID and full URL, open an ID or URL without execution, and show recent queries and Worksheets. App-owned links reuse the current Workbench browser context. |
| Save during a multi-statement Worksheet | Preserve the complete local draft; saving only one statement does not falsely mark the whole Worksheet saved. |
| Existing error and pagination controls | Errors remain visible, busy requests cannot duplicate from shortcuts/buttons, and paged columns/values stay complete. |
