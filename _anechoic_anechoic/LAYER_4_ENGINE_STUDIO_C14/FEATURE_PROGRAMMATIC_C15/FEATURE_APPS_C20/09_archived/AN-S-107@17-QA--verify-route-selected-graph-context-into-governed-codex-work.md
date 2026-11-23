---
atom_family: SPEC
atom_id: AN-S-107
container:
  component: C20
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Verify route selected graph context into governed codex work

# Verify route selected graph context into governed codex work

## Claim checked

CA-M-199 preserves an exact selected graph frontier **and** Tool meaning **when** routing context into Codex work **without** disclosing secrets, bypassing host permission, **or** applying unconfirmed irreversible work.

## Applicable when

Apply **before** accepting **any** Codex action path that begins from selected graph nodes.

## Test case

Select two current nodes whose bounded context includes one unavailable secret value. Seal their IDs, paths, digests, **and** declared selection boundary; route a read question through an existing Skill **and** request an irreversible MCP action **without** the required host confirmation. Then change one selected source **and** repeat the route **without** widening the selection.

## Acceptance criteria

the current question transfers **only** the selected context, omits the unavailable secret, **and** preserves attribution; the irreversible action remains unapplied **without** required host confirmation; the changed source blocks the stale route; **and** **any** Tool **or** host-permission failure remains explicit **and** unmodified.

## Failure disposition

Reject the route **and** preserve the selection frontier, transferred context, secret-handling evidence, invoked Skill **and** Tool contracts, response attribution, host-permission **and** confirmation states, **and** **any** scope widening **or** mutation.
