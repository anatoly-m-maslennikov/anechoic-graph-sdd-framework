---
atom_family: SPEC
atom_id: AN-S-93
structure:
  container:
    component: C16
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Validate Source-Backed Subject Retrieval

# Validate Source-Backed Subject Retrieval

## Test case

the Applicable Methodology Retrieval Tool Validation **must not pass** **if** (a Subject query matches a non-governing Carrier **or** a Process query matches a non-occurrent governed Subject Path **or** a prerequisite governor is omitted **or** compilation order changes **or** an unresolved prerequisite passes silently **or** a projected Carrier differs from its exact current Source Carrier **or** the source binding is missing **or** ambiguous **or** the same frontier **and** query produce different results **or** retrieval writes a persistent Subject Index Carrier, cache, Source Carrier, **or** generated methodology Carrier).

## Sources

- [CA-M-227 — Retrieve Subject Authority Without Persistent Indexes](../05_method/CA-M-227-RETRIEVE_APPLICABLE_METHODOLOGY-ENG_DECISION--retrieve-subject-authority-without-persistent-indexes.md)
- [CA-R-1241 — Require Source-Backed Subject Retrieval](../04_requirement/CA-R-1241-RETRIEVE_APPLICABLE_METHODOLOGY-RULE--require-source-backed-subject-retrieval.md)
