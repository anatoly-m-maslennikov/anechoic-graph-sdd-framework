---
atom_family: TKT
atom_id: AN-T-3275
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:24 +0400
---
## Summary

Enforce Extensions and Local Configuration as Expansions Only

# Enforce Extensions and Local Configuration as Expansions Only

**when** CA-P-946 is Done, **then** the Assignee **must** enforce one Core Meta-Model Requirement under which INSTALLED_EXTENSIONS **and** LOCAL_CONFIGURATION **only** expand registered Core extension points **and** never rewrite Core authority.

## Scope

`((all Active Core Meta-Model Atoms that govern Methodology Source boundaries, extensibility, configuration, definitions, Claims, relations, allowed values, and conflict handling) union (all Active Atoms in INSTALLED_EXTENSIONS) union (all Active Atoms in LOCAL_CONFIGURATION) union (every replacement, archive, or new Atom required solely to establish or satisfy the expansion-only boundary))`

## Definition of Done

the Task is **not done if** (the Core Meta-Model lacks one explicit Requirement that governs the expansion-only boundary for INSTALLED_EXTENSIONS **and** LOCAL_CONFIGURATION **or** **any** Extension **or** Local Configuration Claim redefines, replaces, shadows, weakens, deletes, contradicts, **or** changes the interpretation of a Core Claim **or** **any** Extension **or** Local Configuration Term redefines a Core Term **or** primitive relation **or** **any** Extension **or** Local Configuration Type, allowed value, cardinality, Status, **or** lifecycle rule mutates a closed Core domain **or** a specialization uses an extension point that Core does not register **or** **any** uncertain boundary between valid expansion **and** Core rewriting is resolved below 99 percent confidence **without** the Operator **or** the resulting Core-only, Core-plus-Extensions, **and** Core-plus-Local checks are not reproducible).

## Details

permit Extensions **and** Local Configuration to add Claims, Terms, allowed values, types, methods, evaluations, deliveries, operations, activation decisions, compatibility decisions, **and** priority decisions **only** through Core extension points. keep Extension authority reusable **and** Local Configuration authority Project-specific. classify every other overlap as a conflict or gap rather than implicit precedence.
