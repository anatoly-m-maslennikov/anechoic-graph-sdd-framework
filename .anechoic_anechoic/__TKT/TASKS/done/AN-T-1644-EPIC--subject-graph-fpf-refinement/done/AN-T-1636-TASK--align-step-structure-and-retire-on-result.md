---
atom_family: TKT
atom_id: AN-T-1636
structure:
  container:
    atom: AN-T-1644
  priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: 2026-10-26 17:56:09 +0400
---
# Summary

Align Step structure and retire ON_RESULT

## Objective

Apply the accepted reusable Action and Step structure, move result routing into Conditional Step definitions, and retire ON_RESULT without inventing a replacement relation or control-flow category.

## Details

- Bound the source batch to the Step proposals in .anechoic_tmp/subject-alignment-accepted/steps.json, including the R1513 retirement and directly affected Workflow/Step/Action consumers.
- Keep Action as a separate reusable definition. A leaf Step, including a leaf substep, invokes exactly one Action; a containing or parent Step owns nested Step structure and launches no Action of its own.
- Keep Linear Steps ordered and nonconditional with no Conditional children. A Conditional Step chooses exactly one declared branch and may use Actor input; result-based routing belongs to that Conditional Step definition.
- Retire ON_RESULT and do not replace it with Branch, Fork, Decision, another Relation Type, or runtime mechanics. A terminal outcome ends the Workflow Run and is not another Step or Action.
- Preserve Workflow handoffs, retry/authorization gates, terminal-result meaning, independent Step bindings and existing execution boundaries. No code, runtime, full-suite, release or Git work is included.

### Completion evidence

The accepted source correction is applied. Independent final verification passed.
Evidence: `.anechoic_tmp/subject-alignment-accepted/verify.final.json`,
`verify.final.md`, both publication receipts, and
`graph-final/graph.subject-views.manifest.json`. The four Current-RMEDO views
contain 2,223 sources (792 Core, 405 Methodology, 1,026 Engine), with zero
unmapped Subjects. This is source/projection verification, not runtime execution.

## Definition of Done

- The ON_RESULT definition is retired with no dangling Current consumer that still prescribes it.
- Leaf/containing Step behavior, reusable Action separation, Linear/Conditional structure, one-branch selection and optional Actor input agree across the bounded sources.
- Terminal outcomes and Workflow handoffs remain distinct from Step/Action routing.
- No new relation kind, control-flow entity, execution mechanism or unrelated Operations taxonomy is introduced; actual source evidence is recorded for later integration.
