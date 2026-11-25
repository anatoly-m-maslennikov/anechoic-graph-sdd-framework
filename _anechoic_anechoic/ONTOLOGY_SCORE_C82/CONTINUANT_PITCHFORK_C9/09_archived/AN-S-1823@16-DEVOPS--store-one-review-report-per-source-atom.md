---
atom_family: SPEC
atom_id: AN-S-1823
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Store one review report per source Atom

# Summary

Store one review report per source Atom

## Scope

temporary evidence Carriers of a local RMED Atom review Run.

## Claim

the Run **must** store its temporary evidence under **`=1`** caller-admitted directory using this layout:

- `progress.json`: the original selection, per-Atom path **and** identity, current Step, state, report path, assigned worker, applicable context setting, **and** any blocked **or** unfinished work. a short handoff records the current Atom, completed edits, **and** next work **in** this file.
- `reports/<ordinal>.json`: **`=1`** report per selected Carrier, using its fixed four-digit ordinal. retain the check result **and** later applied corrections **in** this same file.

**every** report **must** contain the source path, carried Atom ID **and** Version, source observation, **all** **`=6`** local check outcomes, concise evidence, confirmed findings, unresolved coverage, applied corrections, **and** current state. a confirmed finding includes its location, source passage, applicable rule, **and** proposed fix. record the original checked source digest once so the fixer can notice concurrent changes.

## Details

shared checking rules **may** be stored once; reviewers receive their relevant actual contents. an existing mechanical report **may** be linked as supporting evidence. separate raw-part files, proposal reports, admission receipts, checkpoint files, **and** closure certificates are **not** required by this Workflow.

states are `pending`, `checked_clean`, `needs_fix`, `fixed_not_rechecked`, **or** `blocked`. `fixed_not_rechecked` records applied corrections **after** **all** initial checks conclude **and** findings are corrected **or** rejected with reasons, **without** claiming a post-fix pass. missing identity, unfinished checks, **or** unresolved findings retain `blocked`, including **when** safe partial corrections were applied.

progress records `reported_result`, `check_complete`, **and** `complete` separately from the derived current `state`. Run totals distinguish reports received, complete initial checks, **and** completed Atoms. preserve original reports **and** their gaps as evidence; reporting **or** editing an Atom does **not** complete unperformed checks. excluded checks are **not** marked as passed.

preserve earlier reports **and** completed work. a workflow-packaging **or** context-budget change alone does **not** invalidate a review of unchanged content under unchanged checking criteria. changed Atom content **or** a changed applicable criterion makes its earlier check historical; this Workflow does **not** automatically recheck it.
