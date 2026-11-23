---
atom_family: TKT
atom_id: AN-T-1791
container:
  component: C14
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 07:55:38 +0400
---

## Summary

SQL completion loses qualifiers and does not escape status values

## Concern

SqlEditor.svelte replaces the typed qualified token using only its quoted column name, and status-value completion does not double embedded apostrophes. Keep M468 unchanged and fix these implementation defects in the follow-up Epic. Verify both through the editor.
