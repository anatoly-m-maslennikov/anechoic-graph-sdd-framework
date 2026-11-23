---
atom_family: SPEC
atom_id: AN-S-1320
container:
  component: C15
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reject temporary state outside project temp

# Reject temporary state outside project temp

## Claim checked

**every** ANECHOIC-controlled PROGRAMMATIC execution **must** confine temporary Carriers created by its components **and** configured dependencies **to** the Project Temporary State root.

## Test case

1. set the working directory **and** ambient host temporary location outside the configured Project Temporary State root.
2. run representative Tool, App backend, **and** MCP fixtures, including their test runner **and** a configured dependency. exercise bytecode creation, caches, temporary workspaces, atomic staging, **and** interrupted **or** denied cleanup.
3. compare the path frontier outside the Temporary State root **before** **and** **after** execution. inspect the applicable source **and** configuration for unredirected temporary-path creation.
4. delete **only** the Temporary State root **in** an isolated fixture **and** compare its protected authority **and** runtime state.
5. make the Temporary State root unavailable **or** make the selected staging
   path fail the same-filesystem precondition **in** an isolated fixture.
   inspect the affected effect **and** its boundary diagnostic.

## Acceptance criteria

**all** of the following **must** hold:

- **every** temporary, scratch, staging, cache, build, Evaluation, **and** cleanup-remnant Carrier is below the configured Project Temporary State root.
- concurrent owners use their declared component **or** run-specific descendants.
- no applicable source **or** configuration uses an ambient **or** hard-coded host temporary fallback.
- deletion of the Temporary State root leaves governed authority, Project Journal history, selected runtime releases, logs, sessions, databases, service state, **and** resumable state unchanged.
- no Python bytecode cache remains below the Runtime State root.
- an unavailable temporary root **or** unsatisfied same-filesystem precondition
  stops the affected effect **and** produces a stable diagnostic identifying
  the creating owner **and** violating path.

## Failure disposition

reject the changed component, test workflow, dependency configuration, **or** release **until** **every** observed **and** statically detectable temporary Carrier uses the Project Temporary State root. report **every** violating path **and** its creating owner.
