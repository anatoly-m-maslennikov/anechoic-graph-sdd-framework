---
atom_family: TKT
atom_id: AN-T-3476
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 3
  updated_at: '2026-11-24T11:39:10.159425+00:00'
---
## Summary

Specify and verify Engine Studio boundaries

## Objective

Review realized code and actual boundaries across Engine Studio, record Contracts and main Tier 1 Decisions with formal claims, and verify the resulting Studio implementation in Lean.

## Work

Create the nine bounded reviews below. Reuse Implementation Verification and report unattached declarations and unsupported cases.

Compile explicit eDSL Model Node, Property, and Relation bindings. Validate the complete admitted Model in Lean before publication, then use that same Model to generate Python runtime modules. Use zero magic; Component boundary Manifests are outside this Model scope.

## Seven-day bug replay

Inventory confirmed functional bug fixes from tickets, Git history, and the worktree for 2026-11-17T15:38:02+04:00 through 2026-11-24T15:38:02+04:00. Distinguish confirmed fixes from candidates and record evidence and coverage limits.

Independently state each supported invariant, translate the actual historical and current code into Lean where supported, and replay against the exact historical buggy revision and fixed state. Scan current sibling paths for the same defect. Record confirmed defects, unsupported cases, and evidence without claiming complete coverage where it is not established.

## Acceptance

Each review records realized code, boundary, Contract, formal Tier 1 Decision or reuse, and unresolved coverage. The final review compares the reviewed Studio implementation in Lean.

The real Model inventory resolves explicitly. Lean validates all bindings before publication, and the same admitted Model generates runtime modules through a release and build gate. Negative closure cases fail; unsupported cases remain open.

The replay inventory accounts for the scoped sources and each confirmed functional fix. Each supported case has an independently stated invariant, code-linked Lean translations, a failing replay on the exact buggy revision, and a passing check on the fixed state. Sibling scans record their scope, confirmed defects, unsupported cases, and evidence. Unresolved cases remain open.

## Findings

Reviewed 51 manifests and 6 seeds. Found 35 current Contract and formal Solution pairs. Fourteen Lean blocks compile and 21 workflow declarations compile. Sixteen records lack executable evidence, including historical definitions.

The C910647071 throughput fixture is absent from the image workspace but present in the mounted Project. C30 has 8 normal and 110 prior cases. C76 has 14 actual source cases. C68 has 2 matched explicit failure traces.

The Studio scan covered 582 source files. It covered 4411 units, 5164 resolved calls, and 3995 unresolved effect cases. It found 1 permitted ambient read and output. The capture excludes tests, assets, and prompt Markdown.

A Lean 4.19 compatibility shim works in scratch. Full conformance remains unsupported.
