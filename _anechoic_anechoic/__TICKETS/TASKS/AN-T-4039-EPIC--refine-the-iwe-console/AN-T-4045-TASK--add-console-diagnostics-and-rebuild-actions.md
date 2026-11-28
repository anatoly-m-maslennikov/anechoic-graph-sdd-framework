---
atom_family: TKT
atom_id: AN-T-4045
container:
  atom: AN-T-4039
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T22:18:31Z"
---
## Summary

Add Console Diagnostics and rebuild actions

## Work

Add a separate Diagnostics tab at the top right of the Console.
Show runtime health, statistics, and available diagnostics.

Provide two backend actions. Rebuild Realization Graph rebuilds the
Realization Graph. Rebuild Project database rebuilds the Project
database from source. Show the state and outcome of each operation.

## Acceptance

Verify the healthy and unhealthy states and their available diagnostics.
Verify that each action requests its intended rebuild and reports
completion or failure.

## Verification

Current Kernel verified Graph-only rebuild, preservation of Atom and
Structure facts, failure preservation, and disabled Graph refusal.
The bound Backend-to-Kernel check returned index health, ingestion
issues, and Worker Runs. All eight Diagnostics browser cases passed.
The shared HTTP check returned live Diagnostics for the bound Project
with the test compiler deadline disabled. The default run timed out
while compiling the Model.
Lean matched the Graph-only rebuild Contract and Solution. The two
generated Kernel cases passed for success and disabled refusal.
See AN-S-3047@34, AN-S-5194@1, and AN-S-3059@63.
