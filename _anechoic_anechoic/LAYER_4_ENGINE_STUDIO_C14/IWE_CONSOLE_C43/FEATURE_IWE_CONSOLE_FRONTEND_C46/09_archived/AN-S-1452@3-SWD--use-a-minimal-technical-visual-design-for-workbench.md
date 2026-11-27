---
atom_family: SPEC
atom_id: AN-S-1452
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-11-05 01:48:39 +0400
---

## Summary

Use a minimal technical visual design for Workbench

## Claim scope

Workbench visual presentation.

## Claim

Use a compact, modern, minimal technical interface with light and dark themes. Reduce repeated headings, large paddings and unnecessary vertical space while keeping controls readable and Zoom available. Put two top-left utility tabs first: `Settings`, followed immediately by `Saved Queries and Worksheets`; current Worksheet tabs follow them. Keep the Settings panel hidden initially; apply Theme and text `Zoom` preferences on page load even while it is hidden. Use one `Hide editor` control for the active Worksheet. Remember the System theme choice. Use text-only font zoom presets `80`, `90`, `100`, `110`, `125`, `150` and `200` percent for all text, including editor text, headings, tabs, menus, buttons and result/status text; remember the selected preset. Do not scale the whole layout or icons. Use a small reusable component palette with accessible labels, loading state and error state. Do not add a large design system.

Put one top-left `Open Saved` button in the toolbar, not an inline open form. Open it with `Cmd+Option+O` into a modal with an autofocus ID/URL input; allow native `Cmd+V` paste, Enter to open without executing SQL, and Escape or Cancel to close. Keep the Saved Queries and Worksheets view as the combined library, and keep status-value completion text-only and unobtrusive.

Light (Day), Dark (Night) and System are selectable theme modes; remember the selected mode.

Use a native dialog for a searchable, keyboard-operated command palette on Cmd+P. List existing UI actions and their available shortcuts, and invoke the same handlers as their controls. Support Arrow Up/Ctrl+P, Arrow Down/Ctrl+N, Enter and Escape. Keep Theme, Zoom and workspace preferences in local storage. Do not add a command-palette framework or another backend.
