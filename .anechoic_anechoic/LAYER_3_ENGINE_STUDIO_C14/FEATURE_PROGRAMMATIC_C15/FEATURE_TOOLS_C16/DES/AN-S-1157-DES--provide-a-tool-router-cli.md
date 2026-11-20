---
identity:
  atom_id: AN-S-1157
context:
  container:
    component: C16
  tier: 1
  lens: DES
state:
  status: active
  version: 23
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Provide a Tool router CLI

# Provide a Tool router CLI

the framework **must** provide one deterministic CLI Tool router that accepts an LLM-selected intent, classifies it as a read-only `finder` intent **or** a mutating **or** materializing `doer` intent, resolves it through as many registered routing steps as required, returns **every** applicable Tool option **without** silently selecting **or** executing one, **and**, **after** the LLM selects an option, returns sufficient machine-readable how-to guidance **to** invoke that Tool correctly, including its command shape, required **and** optional inputs, admissible values, preconditions, effects, success checks, failure modes, **and** representative examples.
