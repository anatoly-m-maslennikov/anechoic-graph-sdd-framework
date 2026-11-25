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
  version: 4
  updated_at: '2026-11-24T11:45:22.222468+00:00'
---
## Summary

Specify and verify Engine Studio boundaries

## Objective

Review realized code and actual boundaries across Engine Studio, record Contracts and main Tier 1 Decisions with formal claims, and verify the resulting Studio implementation in Lean.

## Work

Create the nine bounded reviews below. Reuse Implementation Verification and report unattached declarations and unsupported cases.

Compile explicit eDSL Model Node, Property, and Relation bindings. Validate the complete admitted Model in Lean before publication, then use that same Model to generate Python runtime modules. Use zero magic; Component boundary Manifests are outside this Model scope.

## Operator scope correction

Do not review current code or scan current sibling paths. The seven-day work is a golden corpus of bugs already found and fixed. This direction supersedes conflicting active review and scan instructions above and below. Prior findings remain historical.

## Seven-day bug replay

Inventory confirmed functional bug fixes from tickets, Git history, and the worktree for 2026-11-17T15:38:02+04:00 through 2026-11-24T15:38:02+04:00. Distinguish confirmed fixes from candidates and record evidence and coverage limits.

Build a reusable golden corpus from confirmed fixes. Independently state expected behavior from requirements and evidence. Translate the actual buggy and fixed code into Lean where supported, with exact old and fix provenance. Measure the old failure and fixed pass in Lean. Record unsupported cases and coverage gaps.

## Acceptance

Each review records realized code, boundary, Contract, formal Tier 1 Decision or reuse, and unresolved coverage. The final review compares the reviewed Studio implementation in Lean.

The real Model inventory resolves explicitly. Lean validates all bindings before publication, and the same admitted Model generates runtime modules through a release and build gate. Negative closure cases fail; unsupported cases remain open.

The inventory accounts for the scoped sources and confirmed functional fixes. The reusable golden corpus records exact old and fix provenance, independently established expected behavior, code-linked Lean translations, and measured old failure and fixed pass for each supported case. It identifies explicit coverage gaps and unresolved cases.

## Findings

Reviewed 51 manifests and 6 seeds. Found 35 current Contract and formal Solution pairs. Fourteen Lean blocks compile and 21 workflow declarations compile. Sixteen records lack executable evidence, including historical definitions.

The C910647071 throughput fixture is absent from the image workspace but present in the mounted Project. C30 has 8 normal and 110 prior cases. C76 has 14 actual source cases. C68 has 2 matched explicit failure traces.

The Studio scan covered 582 source files. It covered 4411 units, 5164 resolved calls, and 3995 unresolved effect cases. It found 1 permitted ambient read and output. The capture excludes tests, assets, and prompt Markdown.

A Lean 4.19 compatibility shim works in scratch. Full conformance remains unsupported.
