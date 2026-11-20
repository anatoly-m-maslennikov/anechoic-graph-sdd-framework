---
identity:
  atom_id: AN-S-1136
context:
  container:
    component: C16
  tier: 2
  lens: SWD
state:
  status: active
  version: 26
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Allocate one runtime folder per script

# Allocate one runtime folder per script

give **every** ANECHOIC script **or** executable tool that persists runtime files one dedicated directory beneath the anechoic runtime root. keep its runtime files inside that directory; concurrent runs **may** use bounded run-specific descendants.

do **not** scatter runtime files, write into another script's directory, **or** depend on an unowned shared directory. a shared runtime service owns its own directory **and** clients use its service contract rather than its files.
