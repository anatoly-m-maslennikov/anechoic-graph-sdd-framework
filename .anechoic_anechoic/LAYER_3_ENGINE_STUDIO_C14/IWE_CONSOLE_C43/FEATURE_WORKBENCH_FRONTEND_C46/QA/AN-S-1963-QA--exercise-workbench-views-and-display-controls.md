---
identity:
  atom_id: AN-S-1963
context:
  container:
    component: C46
  tier: 5
  lens: QA
state:
  status: active
  version: 11
  updated_at: '2026-11-12T16:57:55.341412+00:00'
---
## Summary

Exercise Workbench Views and display controls

## Claim

### Prose Claim

Exercise accepted controls through built frontend and real backend, preferring complete browser flows over component internals; shared controls retain native-Workbench acceptance. Format button/palette turns compact SQL into canonical layout (leading commas, uppercase SELECT, lowercase clauses, two-space indent, separate semicolon) without changing quoted identifiers/strings/comments/CTEs/nesting; repeat is stable, creates ordinary unsaved edit/autosave only, sends no Run/Check/Save, and on rejection preserves input/results with error.

Exercise saved View links/Open Saved: preserve count, active ID, edits/results; reopen matching saved ID/URL in its existing View, but do not merge distinct IDs with equal SQL; standalone reload retains identity. Rename non-active tab by context menu and current View by palette from prefilled name; duplicate through both paths creates independent copy without prior result/saved identity and permits independent Run. CA-E-782/783/786 remain detailed owners for rename, result-display and grid; native duplicate is future acceptance.

## Details

Browser-visible checks cover Light/Dark/System persistence and readable focus/text/dark grid; Compact only for explicit `embedded=1` and Comfortable standalone; compact header/layout/settings; independent persisted Interface/Content/whole-interface zoom and Density; separate View input/result, unsaved-close warning, five-second autosave/reload and truthful visible storage failure. With storage blocked, verify that editing still works and a warning explains that reload or close may lose changes. Verify that the embedded marker alone keeps the same Workspace and that missing canonical Project name is a binding error. Exercise Check from Not checked to Valid, edit back to Not checked, then check invalid SQL and see Invalid while the previous rows stay visible. Verify Query editor header/saved link, sole Hide/Show header control, and command-palette-only Open Saved dialog with native paste/Enter-no-execution/Escape-Cancel.

Verify read-only completion from actual dotted schema paths and Header Status quoting, hotkey hints, whole-query Run and Check, rejection of multiple statements, Run & Save storing the exact submitted SQL and Save View preserving the full SQL text, saved resource IDs/URLs/legacy worksheet load, pagination/errors/newline pre-wrap and partial Run `save_error` retaining rows/query ID/prior saved identity/dirty state. Cmd+P search and Arrow Up/Ctrl+P, Arrow Down/Ctrl+N, Enter/Escape invoke the same available controls without mouse. Result header shows name over smaller muted type without changing values.

### Keyboard and untrusted content

Exercise primary flows using keyboard only: visible focus, meaningful names/roles, predictable order, perceivable status and error recovery. Render representative untrusted Project values—markup, links, styles and control characters—in cells and full-value display as inspectable inert data with no execution or capability change.
