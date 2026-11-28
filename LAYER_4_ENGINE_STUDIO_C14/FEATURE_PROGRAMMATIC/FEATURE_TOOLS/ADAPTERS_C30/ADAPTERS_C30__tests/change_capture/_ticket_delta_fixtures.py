"""Ticket and Spec carrier fixtures."""

_TICKET = """---
atom_family: TKT
atom_id: AN-T-2
container: {component: C00}
priority: 2
context: {template: task}
relations: {REFERENCES: [AN-S-1]}
state: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}
---

## Summary

Changed ticket.
"""
_SPEC = """---
atom_family: SPEC
atom_id: AN-S-2
container: {component: C00}
tier: 0
context: {lens: SPEC}
state: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}
---

## Summary

Valid Spec in a Ticket folder.
"""
