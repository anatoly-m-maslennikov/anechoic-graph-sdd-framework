---
atom_family: SPEC
atom_id: AN-S-1986
container:
  component: C14
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Each session can get its active Workflow Runs and history

## Claim

### Prose Claim

Each session must list its own active Workflow Runs and retrieve their recorded history within its selected Project.

Bind each Run to the initiating Project and client session, represented by runtime context `session_id`, and retain that association through continuation. Default listing shows started nonterminal Runs for that Project and session. An explicit Project-wide flag lists all started nonterminal Runs in the same Project. Live Run control follows AN-S-5160. Reading a list or history does not execute, resume or repeat work.

History comes from the existing Project Journal/Event Records with their recorded Run association. Terminal Runs remain available through history under the existing history rules. Query logs, cached query results and their TTL do not define Workflow Run history. The capability is independent of the harness and LLM provider. This Requirement adds no limit on concurrent Runs or new Run Status vocabulary.
