---
atom_family: SPEC
atom_id: AN-S-3424
container:
  component: C20
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 16
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Execute Actions through a replaceable Codex adapter

## Claim

### Prose Claim

This retained contract applies only when AI-Agent execution is separately admitted. It does not enable that execution or claim that its runtime implementation is present.

implement Agentic execution through a replaceable Codex CLI adapter with structured output admission.

## Details

### Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

1. invoke codex exec with argument arrays, stdin prompts, a JSON output schema **and** an explicit isolated working directory. native execution uses a read-only CLI sandbox; the dedicated Docker Agent service uses its container boundary **without** Project mounts. use existing authentication through runtime credential admission, never through an image layer.
2. give the Agent the selected Atom, current rules, the Action prompt **and** phase report, with no other Atom reports.
3. require a structured report plus optional proposed replacement content. validate identity, source hashes, confidence **and** saved check evidence before admission.
4. retain reports **and** candidate content under the dispatch identity before applying changes.
5. bound subprocess duration **and** output reads. timeouts, invalid output **or** missing credentials block execution rather than inventing a pass.
6. keep the executor interface independent of Codex so other harnesses can be added later.
