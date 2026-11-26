---
atom_family: SPEC
atom_id: AN-S-1833
container:
  component: C58
tier: 3
context:
  template: workflow
  lens: DOM/MTD
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T21:55:25.851424+00:00"
---
## Summary

Atom Lifecycle_Archive Atom

## Claim scope

The invocation domain of [Archive one Current Atom](CA-O-10001-PROJECT_CONFIGURATION-ACTION--archive-one-current-atom.md).

## Claim

### Mermaid Scheme

```mermaid
graph TD;
    step1["Archive the selected Current Atom"];
    click step1 "./CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom/CA-O-10008-PROJECT_CONFIGURATION-STEP--archive-the-selected-current-atom.md" "Open Step";
```

### Prose Claim

This Workflow's Purpose is Runtime; its scheme follows AN-S-1709.

#### Input

One exact Current Atom selector. For a folder-backed parent, the caller first archives all recursively contained latest Atoms through independent one-Atom invocations under CA-R-1521, CA-D-461 and CA-D-467. References outside the Carrier tree and older archived revisions are excluded. Stop at the first failure and report completed effects and remaining targets.

The `projectContext` input port binds the Project and applicable model.

#### Output

The `savedArchivedAtom`, warnings, and failure result.

#### Step handoffs

| Step | Receives | Produces |
| --- | --- | --- |
| [Archive the selected Current Atom](./CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom/CA-O-10008-PROJECT_CONFIGURATION-STEP--archive-the-selected-current-atom.md) | selected Atom, `projectContext`,  | `savedArchivedAtom`, warnings or a failure result |

#### Logical switches

| Condition | Behavior |
| --- | --- |
| Entry | Run Archive the selected Current Atom. |
| `savedArchivedAtom` is returned | Complete successfully. |
| A failure result is returned | Stop and report the explicit failure. |

If an Action requests additional input, return its short explanation and requested input dictionary and keep the Workflow pending. Resume with the supplied dictionary; cancellation is allowed while waiting and does not interrupt an Action.
