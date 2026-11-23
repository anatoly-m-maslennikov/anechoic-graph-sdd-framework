---
atom_family: SPEC
atom_id: AN-S-4627
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-30 03:11:57 +0400
---
## Summary

Review code in shared implementation context

## Operation

Shared Implementation Review Step **means** the node of `CA-O-016-PROJECT_CONFIGURATION-WORKFLOW--implement-evaluations-before-required-behavior` that invokes exactly one Action, `CA-O-238-PROJECT_CONFIGURATION-ACTION--review-code-candidate-evidence-and-applicable-method-policy-without-editing`, in explicit Integrated context under `CA-R-1527-CORE_META_MODEL-DEFINITION--define-agentic-step-execution-context`.

- Require explicit `review_phase` preliminary **or** final from `CA-O-231-PROJECT_CONFIGURATION-STEP--prepare-shared-context-implementation-work`. Do **not** derive the phase from absent evidence **or** use the standalone default.
- Bind:
  - the selected Project, bounded request **and** P/Plan;
  - the owned candidate **and** changed paths;
  - direct full `requirements`, `methods`, `evaluations`, **and** `delivery` rows with applicable Project-owned Tier 0 Atom sources;
  - the substantive obligation/coverage map;
  - actual check **and** diagnosis evidence with pending/stale outcomes;
  - relevant inputs **and** permissions; **and**
  - retained findings **and** remaining retry/resource state.
- An optional legacy `method_projection` **may** accompany direct rows but is **not** required.
- Retain the participating session **without** replacing complete source-bound inputs with conversational memory. Revalidate source/candidate/test/input bindings before assessment **and** preserve actual partial findings.
- Pass `preliminary_clear`, `passed`, `findings`, `partial`, **or** `unresolved` directly to `CA-O-016-PROJECT_CONFIGURATION-WORKFLOW--implement-evaluations-before-required-behavior`. Read-only review never edits code, changes authority, grants a retry, **or** launches release; repairs remain in the enclosing implementation Workflow.
- Preserve exact Action/Step revisions, candidate **and** evidence bindings, actual effects, **and** returned results.
