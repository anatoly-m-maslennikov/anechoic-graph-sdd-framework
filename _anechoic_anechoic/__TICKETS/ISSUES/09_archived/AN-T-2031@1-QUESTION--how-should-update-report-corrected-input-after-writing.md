---
atom_family: TKT
atom_id: AN-T-2031
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T03:17:17.749196+00:00'
---
## Summary

How should Update report corrected input after writing

## Question

If promotion requests corrected input after Update has already saved a Draft and archived the Current Atom, should Update stop and report the error with completed effects, or wait for an explicit correction and resume only promotion?

## Details

CA-O-10024@3 describes waiting and resuming promotion. The current Tool returns failure with completed effects. The decision affects only a correction requested after a write. CA-O-10018@2 already reports failure with completed effects. Tracked in CA-P-2791.
