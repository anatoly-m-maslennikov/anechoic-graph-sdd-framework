---
atom_family: SPEC
atom_id: AN-S-1566
container:
  component: C24
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-10-21T23:57:54+00:00'
---
## Summary

Preserve agentic context and bounded handoffs

# Summary

Preserve agentic context and bounded handoffs

## Scope

explicit per-Step Agentic context for the declared Implementation Workflow graph, including its eight Integrated shared-context Steps; separately admitted Isolated invocations retain their own bindings.

## Claim

the Implementation **must** use the Step's supplied Integrated or Isolated context before actual Agentic dispatch; Isolated work uses an assigned subagent with a complete handoff, a fresh admission, and one bounded P subtask estimated below fifteen minutes.

## Details

Unavailable, ambiguous, unsupported, or incomplete context blocks dispatch. A prompt returns its result and retained evidence to its caller; it neither auto-starts a successor nor grants permissions, changes Workflow state, or silently falls back between contexts.
