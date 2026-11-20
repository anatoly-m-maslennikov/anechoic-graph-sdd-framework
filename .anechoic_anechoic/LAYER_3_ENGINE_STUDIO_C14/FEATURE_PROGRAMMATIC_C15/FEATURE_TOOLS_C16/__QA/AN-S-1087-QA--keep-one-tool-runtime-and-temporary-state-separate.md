---
atom_family: SPEC
atom_id: AN-S-1087
structure:
  container:
    component: C16
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Keep one Tool runtime and temporary state separate

# Keep one Tool runtime and temporary state separate

## Claim checked

one Tool places persistent operational state **and** selected releases below
Project Runtime State **and** places disposable state below Project Temporary State.

## Test case

run one Tool **and** one Tool test that create a selected release, log, resumable
state, cache, temporary workspace, staging Carrier, **and** interrupted-cleanup
Carrier. redirect the ambient host temporary location **to** the repository root,
**then** inspect the complete repository, runtime, **and** temporary path frontiers.

## Acceptance criteria

pass **only** **when** the selected release **and** persistent operational Carriers exist
below `.anechoic_runtime/`; **every** disposable Carrier created by the Tool,
test, **or** configured dependency exists below `.anechoic_tmp/`; neither the
repository root nor a source, control, **or** host temporary location gains a
Carrier; deleting temporary state preserves runtime; **and** deleting runtime
preserves governed authority **and** Project Journal history.

## Failure disposition

reject the release **or** runtime layout **until** the boundary is restored.
