---
identity:
  atom_id: AN-S-1559
context:
  container:
    component: C23
  tier: 4
  lens: QA
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary
Check Skill use of the selected Workflow Step

## Claim

### Prose Claim

the Skill-participation Evaluation **must** check that the Skill uses the admitted framework response for the current Step rather than independently choosing a Workflow procedure **or** capability sequence.

#### Fixture and evidence

- fix the Operator request, owning Project, active authority references, routing inputs, admitted Workflow **and** Step, Action inputs, permissions, **and** required result. expose necessary capabilities **and** distinguishable irrelevant alternatives.
- identify the sufficient capability set **or** admitted equivalent alternatives for this bounded fixture. justify it from the Action **and** its bindings; do **not** assert a globally optimal minimum.
- capture the submitted request, framework response, instructions used, capability calls, reported results, **and** **any** continuation request.

#### Acceptance

- the Skill submits the request through the declared framework interface **and** uses the returned current-Step binding; it does **not** maintain another routing dictionary **or** silently substitute another Action.
- capability calls remain necessary for the admitted Action, within authorization, **and** compatible with its required outcome. an irrelevant capability, omitted input, invented source, **or** contradictory instruction yields failure.
- the Skill returns the actual result against its invocation. the executor selects the next Step; the Skill does **not** continue through a remembered **or** locally authored sequence.
- repeating the fixture with a changed admitted Action prompt but the same wrapper interface uses the new bound instructions **without** editing the Skill body. receiving a prompt alone is **not** completion.
- missing evidence **or** an unresolved fixture expectation yields an unresolved result, **not** a successful selection claim.
