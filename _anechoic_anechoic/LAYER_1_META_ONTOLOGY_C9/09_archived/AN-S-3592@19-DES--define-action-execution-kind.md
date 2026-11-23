---
atom_family: SPEC
atom_id: AN-S-3592
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: 2026-10-29 07:45:27 +0400
---
## Summary

Define Action Execution Kind

## Claim scope

the distinction between execution by code **and** execution requiring AI Agent judgment for an Action's declared responsibility.

## Claim

Action Execution Kind **means** the distinction between execution by code **and** execution requiring AI Agent judgment for an Action's declared responsibility.

## Details

- Programmatic: code performs the Action according **to** its specified behavior, **without** delegating interpretation **or** judgment **to** an AI Agent. programmatic interaction with the Operator does **not** by itself make the Action Agentic.
- Agentic: an AI Agent interprets the supplied context **and** instructions **to** perform the Action. the AI Agent **may** call Tools within its admitted authority.
- classify an invocation by the responsibility actually delegated, **not** by whether its transport **or** surrounding executor is implemented **in** code. code that delegates the Action's judgment **to** an AI Agent does **not** make that Action Programmatic.
- the distinction does **not** select the Agent's execution context, grant permissions, **or** change the Action's semantic boundary. Tool calls **do not** by themselves create additional Actions **or** Workflow Steps.
