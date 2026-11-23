---
atom_family: TKT
atom_id: AN-T-2733
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 06:04:43 +0400
---
## Summary

Define the compiler admitted-evidence contract

# Summary

Define the compiler admitted-evidence contract

## Objective

Define the smallest compiler implementation contract that consumes existing
admitted OperatorDecision, Run and effect evidence, while treating Journal
recording as non-blocking for methodology approvals and recovery. The contract
must not accept an authoritative approval flag supplied by the caller.

## Details

This is one bounded contract-design Task with at most 15 minutes of own work,
to activate after CA-P-2629's R1317 source alignment and CA-P-2631's seven
contract reconciliation are independently reviewed. CA-C-586 is an explicit
design hold: the Operator must decide whether O011 obtains the actual
OperatorDecision through the existing interactive MCP loop or whether the
integration gap is deferred and reported. Identify the existing evidence
carriers and current compiler callers only after that decision, preserve result
shapes, partial results, retry accounting, recording_error handling and
no-replay behavior, and separate business Journal append from technical
diagnostics. Do not invent a new input schema, authoritative caller flag,
trusted-evidence contract or runtime behavior in this planning record.
Failed-publication recovery evidence remains separately unresolved until its
current source is adjudicated.

## Definition of Done

Return a source-bound contract proposal naming the admitted evidence fields,
their owner and freshness checks, the caller-visible failure/partial-result
behavior and focused regression boundaries. The proposal must reject a
caller-authoritative approval flag and must not claim CA-C-583 resolved or
runtime/compiler implementation complete. Activate only after CA-C-586 is
answered and CA-P-2629 and CA-P-2631 are reviewed.

## Dependency checkpoint — 23 October 2026

CA-P-2629's four-carrier methodology source package and CA-P-2631's
compiler/shared-run RMED source package are independently reviewed and Done at
99% or higher; CA-P-2632 records the completed identity-safe source
replacement and consumer rebind. This Task remains Backlog because the
Operator's CA-C-586 decision about O011 interactive OperatorDecision
acquisition remains open and compiler implementation has not started. No
compiler contract, caller-authoritative approval flag, source mutation,
binding change or runtime admission is implied.
