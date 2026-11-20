---
identity:
  atom_id: AN-T-1631
context:
  container:
    atom: AN-T-1644
  tier: 4
  template: task
state:
  status: done
  version: 3
  updated_at: 2026-10-26 06:39:23 +0400
---
# Summary

Verify refinement sources and rebuild Subject views

## Objective

After the accepted source-correction Tasks, verify the specific review
findings and rebuild the affected derived Subject views from actual Current
source Atoms.

## Details

Integration Task; estimated own work: up to 15 minutes, excluding any new
source repair discovered during verification.

- Wait for the accepted prerequisite source batches. Record their actual
  completion or explicit deferral; a Draft or Task is not applied evidence.
- Re-read the changed Current definitions and directly affected consumers.
  Verify I01–I08 against the decisions, not against superseded FPF proposals.
- Check new identities and Current reference targets, retained obligations,
  canonical paths, formal Claim representation and the archival Version rule.
- Use the existing local generator and supported project interpreter; do not
  change renderer/tool code. If the accepted source model cannot be represented
  by the existing generator, report that concrete limitation separately.
- Rebuild the affected Core, project Methodology and Engine partition views
  with their stable Projection IDs and actual source IDs/Versions. Coordinate
  one existing generator run with P2653 rather than repeat the same generation;
  P2653 owns the explicit full-graph acceptance. Do not reuse the old count of
  2,238 as a completion target.
- Preserve existing Drafts/Archives and unrelated sources. Terms Graph
  implementation and a new whole-project semantic audit stay out of scope.
- Record which review findings are verified closed and which remain concrete
  source issues. Source checks are not a new runtime/test-suite gate.

### Completion evidence

Source checks V01–V14 PASS; final Core/Methodology/Engine partition views have 799/405/1026 pinned sources and the accepted three sections.

Source verification: `.anechoic_tmp/subject-fpf-refinement/verify.final.md`.
Final source/output pins: `.anechoic_tmp/subject-fpf-refinement/graph-closure/graph.subject-views.manifest.json`.
Actual effect verified; no production tool/runtime implementation or release is claimed.

## Definition of Done

- Each I01–I08 finding has a decision, source disposition and truthful
  verification state.
- Rebuilt views derive from the actual corrected Current sources with
  reproducible source lists, stable IDs and the accepted three-section form.
- No unapproved model change, code/runtime modification or existing-history
  migration was performed.
- Incomplete batches, unsupported representation and remaining uncertainties
  are explicit; no global review of every source body is claimed.
