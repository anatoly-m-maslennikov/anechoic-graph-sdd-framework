---
atom_family: SPEC
atom_id: AN-S-1618
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Record Tool calls within Step Runs

# Summary

Record Tool calls within Step Runs

## Scope

Tool Calls that occur within Step Runs.

## Claim

a Tool Call **means** an invocation of a Tool during execution; **when** it occurs within a Step Run, its execution evidence **must** remain associated with that parent Step Run **in** the canonical Project Journal.

## Details

- retain the invoked Tool, supplied inputs, actual result **or** error, **and** parent Step Run association. preserve call identity **and** timing sufficient **to** distinguish separate attempts; do **not** report an attempted **or** uncertain effect as confirmed completion.
- use authorized references **or** protected representations for secret **or** sensitive inputs under their governing rules; execution tracing does **not** authorize copying secrets into the Journal.
- the parent Step Run invokes its **`=1`** declared Action. its internal Tool calls are execution details, **not** automatically new Steps, sub-steps, Action definitions, **or** Workflow nodes.
- a view **may** display Workflow Run, Step Run, **and** Tool-call evidence as a nested trace; derive the view from the canonical records rather than creating another independently maintained execution history.
- preserve actual ordering **and** parentage **without** inferring concurrency permission, Workflow routing, **or** a new Step Run for **every** Tool call.
