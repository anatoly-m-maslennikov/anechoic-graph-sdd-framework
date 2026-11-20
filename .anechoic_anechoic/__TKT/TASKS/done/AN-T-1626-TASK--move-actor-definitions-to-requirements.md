---
identity:
  atom_id: AN-T-1626
context:
  container:
    atom: AN-T-1644
  tier: 4
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-10-26 06:39:23 +0400
---
# Summary

Move Actor definitions to Requirements

## Objective

Place Actor definitions, including Operator and AI Agent definitions, in R
rather than O, following D08. Retire Actor as an Operations Type.

## Details

Addresses I08. Estimated own work: up to 15 minutes for a bounded first batch.

- Locate Current defining Atoms for Actor, Operator, AI Agent and O/Actor
  participation/authorization policy. Start from R1564/R1565 and their actual
  Current consumers; do not use Subject alone to move every Actor-related Atom.
- Keep existing valid R definitions in R. Definitions use Type Definition;
  normative authorization constraints remain precise R rules.
- For an actual O-to-R move, create a new R Atom ID because Content Role
  changes. Preserve the old version through archival and repair affected
  Current references; do not rewrite a historical Atom into a new role.
- Retire the obsolete definition of O/Type: Actor and correct the admitted O
  catalogue. Do not delete the Actor concept or useful authorization policy.
- Preserve owning scope and applicability unless a concrete evidenced
  correction is required. Do not invent new Actor kinds or instance syntax.
- Record source dispositions, new IDs and verified consumer changes. Split
  additional batches into child Tasks if the full closure exceeds the estimate.

No code, runtime permission change, C/A migration or Terms Graph work is included.

### Completion evidence

Actor, Operator and AI Agent definitions remain R; obsolete R1564 retired, catalogue and seven source consumers corrected. V09 PASS; authorization obligations retained.

Source verification: `.anechoic_tmp/subject-fpf-refinement/verify.final.md`.
Final source/output pins: `.anechoic_tmp/subject-fpf-refinement/graph-closure/graph.subject-views.manifest.json`.
Actual effect verified; no production tool/runtime implementation or release is claimed.

## Definition of Done

- The completed batch has explicit R dispositions for its Actor definitions.
- No definition in that batch remains an O/Actor definition.
- Role changes have new R IDs, predecessor archives and supported Current
  reference updates; authorization obligations have not disappeared.
- Remaining batches or concrete uncertainties are explicit, not called complete.
