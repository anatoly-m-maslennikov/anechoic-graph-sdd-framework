---
atom_family: SPEC
atom_id: AN-S-1899
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 9
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Bound file and subprocess effects

# Summary

Bound file and subprocess effects

plan, validate, **and** bound **every** PROGRAMMATIC file mutation **or** subprocess
invocation **before** applying it; make partial failure diagnosable **and** recoverable
**without** guessing.

## Details

Candidate source: [CA-M-161@11](archive/CA-M-161-PROGRAMMATIC-CORE-METHOD--bound-file-and-subprocess-effects@11.md)

## Applicable when

apply **when** a Tool, App backend service, **or** MCP component writes, replaces, **or**
removes a file, **or** invokes a subprocess.

## Procedure

1. validate the target **and** preconditions **before** mutation.
2. write replacement content through a secure temporary carrier on the
   destination filesystem, flush required bytes, **and** use an atomic replacement
   **only** **where** the supported boundary provides that guarantee.
3. invoke a subprocess with an argument array, explicit timeout, checked exit
   status, controlled environment input, **and** shell execution disabled by
   default.
4. return the target, inputs, outcome, **and** partial-failure context needed for
   diagnosis **or** recovery.

## Outcome

**every** applicable effect has a declared precondition, bounded execution
surface, observable result, **and** explicit recovery limit.

## Failure or stop

stop the effect **when** preconditions fail, an atomicity guarantee is unavailable
**and** no weaker recovery boundary is accepted, **or** subprocess completion,
timeout, **and** exit status cannot be observed.

## Sources

- [Python documentation: `tempfile`](https://docs.python.org/3.14/library/tempfile.html)
- [Python documentation: `subprocess`](https://docs.python.org/3.14/library/subprocess.html)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
