---
atom_family: TKT
atom_id: AN-T-4032
container:
  atom: AN-T-4030
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T21:41:33Z"
---
## Summary

Run paired isolated agent trials

## Work

Use the frozen inputs from AN-T-4031. Run 30 fresh sessions, one
per task and revision. Randomize run order and use neutral revision
labels. Supply only the common instructions, task, and source bundle.
Give each agent the same model, settings, and token budget, with no
memory, tools, or access to other runs. Ask for one unified diff.

## Acceptance

Retain each response with its task ID, revision, and model settings.
Record input, cached input, output, and elapsed time for every run.
Keep failed or missing patches in the trial record.
