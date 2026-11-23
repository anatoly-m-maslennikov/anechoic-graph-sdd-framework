---
atom_family: SPEC
atom_id: AN-S-1541
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Assess every Applicable Methodology conflict while retaining candidates and proposal boundaries.

# Summary

Assess every Applicable Methodology conflict while retaining candidates and proposal boundaries.

## Scope

The deterministic CA-O-153 assessment boundary after one complete selected source frontier.

## Claim

`COMPILE_APPLICABLE_METHODOLOGY` **must** report every detected applicable-methodology conflict and its deterministic candidate proposal without silently dropping, merging, reordering, or editing a source.

## Details

Assessment consumes one CA-R-1839 frontier and produces a digest-bound report of complete boundary, identity, definition, replacement, incompatibility, priority, output-path, stale/currentness, and coverage findings. Every finding retains all involved source references and exactly one deterministic proposed selection or correction proposal; a proposal is neither a selected result nor authority to change a source.

An exact current Operator decision may select an already-existing candidate only when its Journal provenance covers the conflict, proposed selection, and frontier digest. A conflict requiring a source correction produces a separately authorized correction proposal instead. Source ordering, revision freshness alone, configuration precedence, an LLM inference, or a TOML record without the exact canonical Journal decision must not resolve a conflict. Before a selected decision can support publication, the Tool reselects and reassesses the then-current frontier under CA-R-1841.

The result is `{ outcome: "assessed", source_frontier_digest, conflicts, proposals, decision_statuses, evidence_refs }`; an unresolved, unsupported, stale, or incomplete finding sets `publishable: false`. Assessment performs no source mutation, no projection mutation, and no invented Journal event.

### Sources

- CA-O-011 v12 and CA-O-153 v2; CA-O-005 v8.
- CA-P-1442 v1, conflict and approval scenario walk; CA-A-1142 v2, W13 handoff.
