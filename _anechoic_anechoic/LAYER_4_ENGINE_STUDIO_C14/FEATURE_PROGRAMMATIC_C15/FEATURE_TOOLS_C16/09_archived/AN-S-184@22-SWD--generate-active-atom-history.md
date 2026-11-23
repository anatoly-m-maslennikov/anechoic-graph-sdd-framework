---
atom_family: SPEC
atom_id: AN-S-184
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 19:59:39 +0400
---
## Summary

Generate active Atom history

# Generate active Atom history

generate the active Atom history through this procedure:

1. resolve the configured Artifact timestamp timezone **and** the authoritative first-parent Git revision frontier. use calendar dates **in** that timezone; never use carrier filesystem creation **or** modification times as historical evidence.
2. for **every** calendar date from the first authoritative revision through the requested end date, select the last authoritative revision at **or** **before** that date's end **and** carry the preceding revision forward across dates **without** a new revision.
3. at **every** selected revision, resolve the structural topology, Type registry, canonical Atom addresses, **and** registered lifecycle placement from that revision. count **every** active Atom exactly once **and** fail closed **when** the historical revision cannot be interpreted **without** a declared compatibility rule.
4. for **every** reporting date compute one grand total **and** complete independent rollups by canonical Type, structural level, **and** structural unit. emit registered zero-count members **and** require **every** rollup for that date **to** sum **to** its grand total.
5. bind the output **to** `<project-control-root>/biz_atoms_active_history.md` **and** emit one stably ordered long-form table with `date`, `dimension`, `member`, **and** `active_atom_count`, **where** `dimension` is exactly `total`, `type`, `structural_level`, **or** `structural_unit`.
6. bind the Git frontier, reporting range, timezone, historical compatibility configuration, generator version, **and** source digests; replace the Projection atomically, record the completed rebuild through the Work Journal, **and** require byte-stable semantic output from the same frontier **before** reporting the history current.
