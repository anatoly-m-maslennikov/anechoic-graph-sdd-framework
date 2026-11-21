---
atom_family: TKT
atom_id: AN-T-1629
container:
  atom: AN-T-1644
priority: 2
context:
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-10-26 06:39:23 +0400
---
# Summary

Align formal Graph Rule addresses with canonical Subjects

## Objective

Repair I04's retired Subject addresses in operative Graph Rule YAML and its
directly relevant schemas/examples without changing the rule conditions.

## Details

Estimated own work: up to 15 minutes. Follow P2640–P2643's accepted definitions.

- Read Current R2003/R2149 and the relevant R1997/D637 clauses.
- Replace retired Entity/Node and Subject/Domain/Node addresses with the
  actual accepted full canonical paths for the same selected kinds.
- Preserve immediate-bearer cardinality, inclusion of dependent occurrences
  missing an edge, Tier comparison, scope ancestry and accepted exceptions.
  A prefix repair is not permission to redesign any of those conditions.
- Apply the accepted logical/formal Claim distinction without imposing
  a universal Markdown section or converting formal Atoms into configuration.
- Preserve historical carriers; actual Current changes get normal predecessors.
- Record exact changed selectors and evidence that their intended domain and
  condition remain unchanged. Ask for any genuinely ambiguous target.

### Completion evidence

R2003@9 restores broad Subject/Graph Node bearer domain; R2149@8, R1997@11 and D637@18 use canonical addresses without changing the intended constraints. V13 PASS.

Source verification: `.anechoic_tmp/subject-fpf-refinement/verify.final.md`.
Final source/output pins: `.anechoic_tmp/subject-fpf-refinement/graph-closure/graph.subject-views.manifest.json`.
Actual effect verified; no production tool/runtime implementation or release is claimed.

## Definition of Done

- The completed operative selector and example set uses accepted canonical
  paths to the same intended targets.
- Rule logic and existing boundary exceptions are preserved.
- No new selector language, rule type, defaults or runtime evaluator was added.
- Actual source corrections are recorded separately from this Plan.
