---
atom_family: TKT
atom_id: AN-T-1435
container:
  atom: AN-T-1436
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Resolve graph authority from declared sources

## Objective

Graph-authority refresh resolves its finite source closure through the selected Project's declared authority roots instead of obsolete hardcoded folders.

## Details

Estimated own work: up to 15 minutes. Inherit CA-P-2270's independently accepted contract and authority gates. Implement only the refresh consumer and focused tests; split further work before exceeding this bound. Root owns Plans and Git.

Reuse the existing Project Structure reader and declared source ownership. Preserve the finite source-ID selection, exact version/hash checks, duplicate and missing-source refusal, and selected Project boundary. Do not infer identity from filenames, restore archived sources, choose a new Settings policy, add legacy fallback, or weaken stale-source checks. Report any remaining closure mismatch rather than automatically repinning it.

No source metadata/content/Subject migration, runtime activation or live publication is included. Independently verify the changed code, complete current closure result and stale/missing/ambiguous source refusal. Broader admission remains blocked independently by legacy source defects and missing current release authority.

### Acceptance

Implementation committed as 92261be4e. The finite 26-source graph authority closure resolves through declared Core ownership; path-only manifest changes retain IDs, versions and hashes. Focused graph tests 8/8 passed in both worker and root runs; validator checkpoint 309/309 and relation tests 7/7 passed. Independent review accepted the narrow resolver; missing, duplicate, unsafe and escaped source roots still refuse. No Release/runtime acceptance is implied; CA-D-572 remains unresolved under the parent.

### Definition of Done

The Plan is **not** Done if refresh still uses obsolete authority roots; current declared sources cannot be resolved; focused closure and refusal checks fail; a source mismatch is hidden by fallback or blanket repinning; independent verification is missing; or runtime/source-migration readiness is claimed from this bounded consumer correction.
