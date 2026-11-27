---
atom_family: TKT
atom_id: AN-T-3987
container:
  component: C9
priority: 2
context:
  template: task
  label: Task
state:
  status: "backlog"
  version: 1
  updated_at: "2026-11-26T13:31:56.520213+00:00"
---
## Summary

Define Concern Path syntax and classification traversal

## Work

Update the Concern Path Manifest and its validator. Admit `/` for containment, `//` for specialization, `.` for a Property, `:=` for a declared value, and `()` for a grouped qualifier. Admit `>|` toward the classifier and `|<` toward the classified members. Keep the compact notation in Concern Paths.

## Acceptance

Use `atom.state.status >| status group := current` as the forward example. Test the matching `|<` traversal in reverse. Verify `:=` selects a declared value. Retire standalone colon qualification from Current authoring.

## Progress

Implemented and tested the approved Concern Path syntax in both classification directions. The candidate Model compiles with the updated Path Manifest. Promotion and Model-level value resolution remain open.

The Path Manifest names Concern Path Notation and retains the approved example. Status Group is a derived projection field. The Model has no Status Group classifier for semantic lookup through the example.
