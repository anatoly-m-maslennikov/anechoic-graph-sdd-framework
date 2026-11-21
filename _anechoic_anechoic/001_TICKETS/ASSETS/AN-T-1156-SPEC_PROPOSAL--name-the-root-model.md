---
atom_family: TKT
atom_id: AN-T-1156
container:
  component: C00
priority: 2
context:
  template: Spec Proposal
state:
  status: in_queue
  version: 2
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Name the root Model

## Decision

The root is Model, not Formal Model. Rename the root label and proposed canonical selectors from Formal Model::... to Model::..., preserving their structure and meaning. The storage fields subjects.governs and subjects.depends_on retain their names. The existing Subject definition is not silently turned into the new Model definition. Historical proposal records and the completed FPF report retain their recorded wording.

## State

Proposal and prepared Draft updates only. Current methodology, governing configuration, historical reports and implementation are unchanged.
