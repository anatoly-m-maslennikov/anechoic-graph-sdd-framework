---
atom_family: SPEC
atom_id: AN-S-1084
container:
  component: C34
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject a service dependency outside the Tool runtime

# Reject a service dependency outside the Tool runtime

## Claim checked

A registered background service cannot load Framework implementation from the canonical source, a non-Tool runtime descendant, temporary state, **or** another Project path.

## Test case

Install a service registry whose Python command addresses a script **in** the repository outside `.anechoic_runtime/tools`; invoke dry-run.

## Acceptance criteria

the Tool returns one stable dependency-boundary diagnostic **before** starting a process **or** creating service runtime state. Git, governed source, registry, runtime, temporary state, **and** the external script remain byte-identical.

## Failure disposition

Reject delivery **if** the external script is accepted, read as framework dependency, copied implicitly, **or** started; **or** **if** rejection mutates project state.
