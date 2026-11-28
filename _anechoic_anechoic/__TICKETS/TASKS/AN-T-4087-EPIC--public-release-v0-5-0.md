---
atom_family: TKT
atom_id: AN-T-4087
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T08:08:02+00:00'
---
## Summary

Public Release v0.5.0

## Objective

Publish ANECHOIC v0.5.0 from an exact, verified Current release candidate.

## Scope

Use existing Tickets for fixes. Record their release disposition here.
The required gates and the existing Local Release prerequisites remain
in effect. The Operator owns public publication.

Default scope is Current. These items can follow the release. Obtain
Operator approval for any deferral that affects an existing gate.

- Generated TypeScript (AN-T-3490) and broader Lean coverage (AN-T-3485).
- Beta OpenAPI packaging (AN-T-4076) and the MCP SDK evaluation (AN-T-4080).
- Studio Spec cleanup (AN-T-4074).

The current Active Continuant carriers can ship if the candidate
compiles and passes its canary. Their migration remains under
AN-T-3985 and AN-T-4007.

## Tasks

1. AN-T-4088 · Clear the v0.5.0 Static and Code Access blockers
2. AN-T-4089 · Verify the formal Model in the v0.5.0 candidate
3. AN-T-4090 · Verify Current Console, MCP, and OpenAPI
4. AN-T-4091 · Verify fresh installation and upgrade
5. AN-T-4092 · Seal and qualify the exact v0.5.0 candidate
6. AN-T-4093 · Prepare v0.5.0 release notes and review the PR
7. AN-T-4094 · Publish and verify v0.5.0

## Done when

Compare the shipped implementation and tests with the bound Formal
Specs. Resolve the findings before release.

All required receipts identify the same sealed source and candidate
image. The Operator approves the reviewed release, and the public
main commit, version, PR, and first Project smoke are verified.
