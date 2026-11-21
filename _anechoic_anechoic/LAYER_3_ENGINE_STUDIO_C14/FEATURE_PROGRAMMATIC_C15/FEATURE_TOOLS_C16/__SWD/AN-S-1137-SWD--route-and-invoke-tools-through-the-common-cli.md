---
atom_family: SPEC
atom_id: AN-S-1137
structure:
  container:
    component: C16
  tier: 2
context:
  lens: SWD
state:
  status: active
  version: 30
  updated_at: 2026-10-27 19:59:39 +0400
---
## Summary

Route and invoke Tools through the common CLI

# Route and invoke Tools through the common CLI

use this flow for **every** Tool invocation:

1. the LLM declares the intended capability **without** naming an implementation; the router classifies it as `finder` **or** `doer` **and** **may** refine it **to** a registered subtype such as `checker`.
2. the router resolves as many registered decision steps as required **and** returns **every** applicable Tool with identity, purpose, inputs, preconditions, effects, success checks, failure modes, command shape, **and** representative examples.
3. **after** the LLM selects one Tool, pass either composable structural-unit, Type, **and** subtype filters **or** explicit canonical Atom filenames through the common target selector **and** return the resolved target set **before** execution.
4. execute the selected Tool from its selected immutable release under `.anechoic_runtime/tools`. use other owned `.anechoic_runtime/` descendants for persistent logs, sessions, databases, service state, **and** resumable state. use `.anechoic_tmp/` **only** for disposable scratch, staging, caches, builds, Evaluations, atomic-write intermediates, **and** cleanup remnants. **every** Finder, including **every** Checker, receives no mutation capability **and** **must not** mutate authoritative sources **or** derived outputs, while **every** Doer first returns a complete mutation-free dry run **and** **then** writes **only** its declared authoritative source **or** derived output **after** explicit application.
5. return the common result envelope, stable diagnostics, exit status, resolved targets, observed effects, **and** applicable currentness information.
