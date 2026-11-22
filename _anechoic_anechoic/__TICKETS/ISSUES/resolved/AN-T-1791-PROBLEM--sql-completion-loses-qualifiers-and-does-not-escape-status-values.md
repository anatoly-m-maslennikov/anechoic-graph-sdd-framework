---
atom_family: TKT
atom_id: AN-T-1791
container:
  component: C14
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-11-11 02:40:22 +0400
---

## Summary

SQL completion loses qualifiers and does not escape status values

## Concern

SqlEditor.svelte replaces the typed qualified token using only its quoted column name, and status-value completion does not double embedded apostrophes. Keep M468 unchanged and fix these implementation defects in the follow-up Epic. Verify both through the editor.

## Resolution

P2812 corrected qualifier preservation and apostrophe handling. Integration-owner code review and the real-image browser scenario passed; no Run, Check or Save was issued during completion. Historical I8 evidence remains context, not a Current governing link. See P2924.
