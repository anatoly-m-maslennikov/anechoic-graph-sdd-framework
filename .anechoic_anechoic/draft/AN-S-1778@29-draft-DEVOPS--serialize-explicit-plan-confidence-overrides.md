---
identity:
  atom_id: AN-S-1778
context:
  container:
    component: C00
  tier: 3
  lens: DevOps
state:
  status: draft
  version: 29
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Serialize explicit Plan confidence overrides

## Claim scope

explicit Plan Autonomous Confidence Threshold overrides in Plan Atom Markdown File Carriers.

## Claim

an explicit Plan Autonomous Confidence Threshold override **must** use the top-level integer frontmatter field `autonomous_confidence_threshold` **in** that Plan Atom's own mandatory Markdown File Carrier.

- a Hub uses that same file, **not** a separately identified Objective **or** Epic settings file.
- omit an unselected override **without** copying its inherited value; the mandatory file requirement does **not** turn inheritance into a local selection.
- retain an explicit override even **when** it equals the inherited value.
- `epic_overrides` is **not** an alternative canonical encoding.
