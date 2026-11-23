---
atom_family: TKT
atom_id: AN-T-2011
container:
  component: C45
priority: 2
context:
  template: problem
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 02:31:44 +0400
---

## Summary

Workbench omits the Framework model from query schema

## Concern

The live image exposes 68 atoms columns with no content.* columns. Its generated canonical Relation registry is empty too. R2726 and M500 require Current-model-declared Content and regenerated Role/Form applicability; a successful count(*) query does not satisfy that contract.

SourceReader selects only role directories reached through Current Project Scope Unit Declarations. The current reader returns 36 units and no CORE_META_MODEL or METHODOLOGY_SOURCES because R2648 FRAMEWORK_METHODOLOGY is archived. The Framework declarations remain on disk outside that selected Project tree, so neither schema compiler receives them. A live audit query for R2498/R2499/R2478 returns no rows because these files are outside its inventory; it is not proof they are queryable.

## Details

P2866 must bind the authoritative Current Framework-model input independently of the Project instance inventory, then verify declared Content, Role/Form applicability, relations and affected-source refresh through query_run. Confirm the established source/configuration with the Model owner; do not restore retired Scope declarations, infer authority from arbitrary copied directories or count copied/staged documents as Current sources. The running Header-only queries remain available.

Evidence: .anechoic_tmp/CA-P-2791/CA-P-2811/query_schema.json and .anechoic_tmp/CA-P-2791/CA-P-2866/declaration-content-issues.json.
