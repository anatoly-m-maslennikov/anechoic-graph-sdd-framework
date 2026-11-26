---
atom_family: SPEC
atom_id: AN-S-1735
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 21
  updated_at: '2026-11-25T21:38:51.247175+00:00'
---
## Summary

Validate Workflow Run definition bindings

## Claim

### Prose Claim


a Workflow Run's declared definition bindings **and** revalidation evidence.


the Evaluation **must** check a Workflow Run's declared definition bindings **and** revalidation evidence under AN-S-1617.

## Details

- A Workflow Run identifies its exact admitted Workflow graph, Step Atom, Action, and called Workflow Revisions. Each Step Run identifies its exact Step Atom Revision. A leaf Step Run also identifies the exact Action or Workflow Revision it invoked. A containing Step Run groups its nested Step Runs without an invocation binding of its own. Accept this binding evidence.
- change, withdraw, **or** make a bound definition unavailable **before** another dispatch **or** recovery: require a pause for revalidation, **not** silent use of a different Revision.
- provide a recorded revalidation that identifies admitted remaining-work bindings, checks compatibility with completed effects **and** inputs, **and** satisfies current authorization: admit continuation subject **to** remaining execution gates.
- supply missing compatibility evidence, revoked permission, **or** stale target inputs: keep the affected execution blocked even **if** definition binding is complete.
- revise a definition during an in-flight Action: retain the actual binding **and** outcome, follow the admitted interruption policy, **and** require revalidation **before** further dispatch.
- rewrite completed Step bindings, replay completed effects automatically, reset retries, **or** treat a recorded historical binding as continuing permission: reject.

these checks establish whether the binding evidence satisfies the model. a recorded assertion alone does **not** prove that an executor performed the required checks.
