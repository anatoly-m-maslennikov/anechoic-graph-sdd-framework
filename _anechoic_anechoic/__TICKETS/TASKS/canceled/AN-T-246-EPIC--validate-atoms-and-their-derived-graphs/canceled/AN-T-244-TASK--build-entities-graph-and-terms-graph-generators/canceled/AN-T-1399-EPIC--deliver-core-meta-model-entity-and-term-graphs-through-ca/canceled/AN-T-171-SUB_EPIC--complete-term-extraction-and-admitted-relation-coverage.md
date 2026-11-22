---
atom_family: TKT
atom_id: AN-T-171
container:
  atom: AN-T-1399
priority: 2
context:
  template: task
  label: Sub-epic
state:
  status: canceled
  version: 8
  updated_at: '2026-11-20T20:26:59.462448+00:00'
---
# Summary

Complete term extraction and admitted relation coverage

## Objective

Complete the bounded child work for term extraction and admitted relation coverage.

## Details

Own work: none. This group is complete only through its direct child Plans.

Direct children:

- [CA-P-1879](06-CA-P-1878-EPIC--complete-term-extraction-and-admitted-relation-coverage/01-CA-P-1879-TASK--implement-current-term-hierarchy-extraction.md) — Implement current term hierarchy extraction.
- [CA-P-1880](06-CA-P-1878-EPIC--complete-term-extraction-and-admitted-relation-coverage/02-CA-P-1880-TASK--check-admitted-relation-coverage-and-record-bounded-gaps.md) — Check admitted relation coverage and record bounded gaps.

Any required relation gap gets a separately admitted bounded direct child before implementation and blocks the golden fidelity Task. This group cannot finish while a required gap remains.

Inherited safeguards: the main Epic's current source authority, graph separation, Property ownership, owned-Core selection, runtime identity and truthful evidence apply. Keep the Operator's explicit 90% confidence threshold.

### Definition of Done

the Plan is **not** Done **if** ((any direct child is **not** Done) **or** (required group evidence is missing, blocked, failed, stale **or** conflicting) **or** (a required relation gap is unresolved **or** lacks its admitted bounded child)).
