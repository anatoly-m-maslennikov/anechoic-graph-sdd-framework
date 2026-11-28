---
atom_family: TKT
atom_id: AN-T-3917
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T07:48:09+00:00'
---
## Summary

Total Refactoring

## Objective

Eliminate all import violations across the Project. Preserve behavior at supported contracts.

## Work

1. AN-T-3918 inventories and assesses the violations.
2. AN-T-3919 applies the decisions in the recorded order and verifies each
   changed boundary.
3. Refactor package boundaries, Python data ingress, and authored JavaScript
   under the agreed source-size and code-cleanup rules. Use Pydantic for every
   structured Python model across the Project. Preserve behavior at supported
   Contracts.
4. Run the authorized parallel Beta path with independent candidate and
   Current images. Enforce `enforce_source_languages = true` for Beta
   verification and eventual cutover. Compare supported Contracts and
   performance before promotion. Keep Current until cutover.
5. Run focused functional tests during the work. Finish with the packaged
   end-to-end suite and one MCP canary.

## Static alignment

Ruff lint passed, and all 2,129 files in the formatter scope passed.
The 300/45 check found no violations. The Pydantic check reported zero
blocking findings and 38 advisory candidates. All 31 native MCP
regression tests passed.

The 79-character limit and packaged end-to-end verification remain open.

## Follow-up

1. [AN-T-3923](AN-T-3917-EPIC--total-refactoring/AN-T-3923-TASK--batch-full-duckdb-rebuilds-in-one-transaction.md) batches full DuckDB rebuilds.
2. [AN-T-3922](AN-T-3917-EPIC--total-refactoring/AN-T-3922-TASK--port-the-beta-rebuild-fixes-to-the-main-checkout.md) ports the Beta rebuild fixes.

## Spec task queue

- [ ] **Clean up the active Specs.** After AN-T-3919 implementation verification
  and cutover, keep the main decisions, merge overlaps, and move decisions to
  the appropriate tier or Component. Remove obsolete active Specs and preserve
  archived revisions.
- [ ] **Verify the Specs against the implemented revision.** After cleanup,
  check the affected Specs, including Manifests, Contracts, Solutions, and
  bindings, against the exact revision that passed packaged verification.
  Record the revision and evidence. Resolve discrepancies and add missing
  governing decisions. Use applicable Tier 0–3 Atoms, then ask the Operator
  if uncertainty remains.

## Pydantic tasks

- [ ] **Generate interface schemas from Pydantic contracts.** Use the
  owning models to generate JSON Schema and the corresponding TypeScript
  types. Start with `query_run`, shared by HTTP and MCP. Check drift in Static
  and compare the generated contract with the supported wire format.
- [ ] **Validate readiness and lifecycle states with tagged unions.** Use the
  existing discriminator to define fields for each state. Check recognizable
  untagged model unions in the linter. Test supported and invalid states.
- [ ] **Use direct JSON and reusable batch validation.** Check for
  decode-then-validate calls and TypeAdapter construction in loops. Change
  eligible call sites and benchmark the worker path. Preserve validation
  and error behavior.

## Acceptance

- The whole-Project Realization Graph and import lint report zero violations,
  including production imports from directories ending in `__tests`. The zero
  result is required after the superseded active source is retired at cutover.
- The source linter, model validation, TypeScript coverage, and code-cleanup
  checks pass. Every structured Python model uses Pydantic without unsupported
  behavior changes.
- Candidate closure passes while Current coexists. The full packaged
  end-to-end suite and one final MCP canary pass before cutover. The strict
  source-language gate is enabled for Beta and eventual cutover.
- Both Spec tasks are complete.
