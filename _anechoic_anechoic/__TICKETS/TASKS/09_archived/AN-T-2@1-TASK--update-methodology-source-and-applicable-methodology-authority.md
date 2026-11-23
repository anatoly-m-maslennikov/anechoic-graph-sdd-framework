---
atom_family: TKT
atom_id: AN-T-2
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: 2026-08-28 21:11:50 +0400
---
## Summary

Update Methodology Source and Applicable Methodology Authority

# Update Methodology Source and Applicable Methodology Authority

**when** CA-P-912 is Done, **then** the Assignee **must** make Methodology Source and Applicable Methodology authority preserve exact source identities through deterministic Projection relations.

## Scope

`((every CA-P-905 frontier entry assigned to METHODOLOGY_SOURCE_AND_APPLICABLE_METHODOLOGY) union (every replacement or new authority Atom created from such an entry))`

## Definition of Done

the Task is **not done if** (Methodology Source is modeled as an independent Entity, Property, or `Artifact/Revision/Methodology Source` descendant **or** Methodology Source is not the target role of DERIVED_FROM from Applicable Methodology Revision to an exact Artifact Revision **or** Applicable Methodology is not both Projection and Relational Artifact **or** one Applicable Methodology member acquires new Atom or independent Artifact identity instead of preserving its exact source Atom Revision **or** compilation includes CAP, Draft, Archived, or non-RMEDO Atoms **or** compilation synthesizes or merges Claims **or** unresolved conflicts do not fail closed for exact Operator resolution in source authority **or** current compilation requires an Installed Extensions source when none is active **or** CORE_META_MODEL or LOCAL_CONFIGURATION is treated as a Scope Unit subtype rather than a named Scope Unit instance **or** any replaced conflicting authority remains active).

## Details

select current active RMEDO Atom Revisions from the exact Core Meta-Model and Local Configuration source revisions. preserve Atom ID, revision, and authority ownership. permit future selected Extension revisions without requiring an installed-extension layer now. leave projected files, source Carrier paths, formats, and concrete compilation folders entirely to CA-P-913 Delivery authority.
