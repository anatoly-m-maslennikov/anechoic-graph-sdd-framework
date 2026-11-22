---
atom_family: SPEC
atom_id: AN-S-1841
container:
  component: C9
tier: 3
context:
  template: workflow
  lens: DES/DOM
state:
  status: active
  version: 2
  updated_at: 2026-11-11 14:19:47 +0400
---
## Summary

Atom Lifecycle_Update Atom Directly

## Claim scope

The invocation domain of [Apply one Direct Atom Update](CA-O-10000-PROJECT_CONFIGURATION-ACTION--apply-one-direct-atom-update.md).

## Claim

### Mermaid Scheme

```mermaid
graph TD;
    step1["Apply the requested Direct Atom Update"];
    click step1 "./CA-O-10023-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom-directly/CA-O-10022-PROJECT_CONFIGURATION-STEP--apply-the-requested-direct-atom-update.md" "Open Step";
```

### Prose Claim

This Workflow's Purpose is Runtime; its scheme follows [CA-R-1570](../../CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1570-CORE_META_MODEL-RULE--keep-workflow-graphs-separate-from-step-bindings.md).

#### Input

One exact Atom selector and the requested property changes.

The `projectContext` input port binds the Project and applicable model.

#### Output

The `savedAtom`, warnings, and failure result.

#### Step handoffs

| Step | Receives | Produces |
| --- | --- | --- |
| [Apply the requested Direct Atom Update](./CA-O-10023-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom-directly/CA-O-10022-PROJECT_CONFIGURATION-STEP--apply-the-requested-direct-atom-update.md) | selected Atom, requested changes, and `projectContext` | `savedAtom`, warnings or a failure result |

#### Logical switches

| Condition | Behavior |
| --- | --- |
| Entry | Run Apply the requested Direct Atom Update. |
| `savedAtom` is returned | Complete successfully. |
| A failure result is returned | Stop and report the explicit failure. |

If an Action requests additional input, return its short explanation and requested input dictionary and keep the Workflow pending. Resume with the supplied dictionary; cancellation is allowed while waiting and does not interrupt an Action.
