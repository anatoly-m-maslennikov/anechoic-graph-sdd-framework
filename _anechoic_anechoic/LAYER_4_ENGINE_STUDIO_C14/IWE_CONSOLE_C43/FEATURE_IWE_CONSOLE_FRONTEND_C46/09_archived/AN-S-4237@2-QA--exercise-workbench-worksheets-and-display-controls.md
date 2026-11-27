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
  version: 2
  updated_at: 2026-11-05 01:40:28 +0400
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
| Compact navigation | `Settings` is the first top-left utility tab; `Saved Queries and Worksheets` is immediately to its right; current Worksheet tabs follow. Theme and Zoom work while the Settings panel is hidden. |
| Text zoom | Editor, buttons, tabs, menus, headings, result and status text change size. Layout dimensions and icons are not multiplied. |
| Two Worksheets | Inputs and displayed results stay with their own tabs. Closing unsaved input asks first. |
| Five-second autosave and reload | Whole scripts, current Worksheet names and open-tab state restore without clicking Save. Browser unload flushing is best effort; storage failures are visible and are not false success. |
| Current Worksheet name | The Operator can rename a current Worksheet; five-second browser autosave and reload retain that name. Save Worksheet copies the optional name into a new entry without renaming an existing saved item. |
| Native window close warning | Unsaved input uses the browser warning when the browser permits it; no cross-browser controller is added. |
| Hide editor | One `Hide editor` control hides and reopens the same input while preserving its script and cursor in the current page. |
| Open Saved modal | The one top-left `Open Saved` button and `Cmd+Option+O` open a modal with an autofocus ID/URL input. Native `Cmd+V` paste is accepted; Enter opens without execution; Escape and Cancel close it; no inline open form is shown. |
| Completion | Actual tables and columns are offered, including quoted dotted/spaced content columns. A prefix such as `status = 'Act` offers and inserts `Active` with correct quoting. The editor does not execute SQL or create a saved record for suggestions. |
| Cursor actions | Run and Cmd+Enter execute the current statement; Check and Shift+Cmd+Enter check it; Save saves it; Save Worksheet saves the entire script. |
| Saved resource links | Show ID, optional creation name and full URL, open an ID or URL without execution, and show recent queries and Worksheets in one tab. App-owned links reuse the current Workbench browser context; saved items are not renamed. |
| Save during a multi-statement Worksheet | Preserve the complete local draft; saving only one statement does not falsely mark the whole Worksheet saved. |
| Existing error and pagination controls | Errors remain visible, busy requests cannot duplicate from shortcuts/buttons, and paged columns/values stay complete. |
