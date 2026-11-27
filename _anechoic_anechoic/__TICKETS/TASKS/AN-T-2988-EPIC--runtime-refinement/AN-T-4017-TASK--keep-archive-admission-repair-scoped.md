---
atom_family: TKT
atom_id: AN-T-4017
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T19:05:24Z"
---
## Summary

Keep Archive admission repair scoped

## Work and acceptance

Reproduce the Archive admission rejection from AN-T-4012. Surface
the exact Kernel reason, Atom refs, and carrier paths. Handle invalid
Archive records through ingestion issues. Repair affected Archive
rows and relations without rebuilding Current and Draft.

Verify cold Archive admission on the same frozen Project. Cover
duplicates within Archive and across the live boundary. Confirm
that valid rows remain queryable and no full native rebuild starts.

## Evidence

The frozen Project admits `AN-S-1860@37` as Current from
`_anechoic_anechoic/_DES/`. The Archive capture returns the same exact
revision from `LAYER_4_ENGINE_STUDIO_C14/09_archived/`. Passing those
rows through Kernel's duplicate check reproduces
`Archive Atom collides with another Atom phase`.

The frozen Project also has two Archive carriers for `AN-S-1081@27`.
Cover this same-phase conflict separately from the cross-phase case.

The startup API fixture also reaches foreground Ready but fails
Archive loading. The trace shows `_finish_archive` receiving no
capture result and then indexing it. The control run reproduced
this with the original startup performance code.
