---
atom_family: TKT
atom_id: AN-T-105
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 20:57:35 +0400
---
## Summary

Distinguish Prompt and Module execution

# Summary

Distinguish Prompt and Module execution

## Decision

Implementation > Package > Prompt. A Prompt is executable instructions for an LLM AI Agent engine. A Module is executable by its language engine, through compilation or interpretation as applicable. Prompt and Module are logical Implementation parts; their File or other Carriers are representations, not execution engines. Asset covers non-executable Implementation content; Prompt is not classified as Asset merely because its stored text file is not executable by the operating system. This refines the previous instructional-purpose definition without introducing another Runtime kind or Relation Type.

## State

Updates review Drafts only. Current sources, code and runtime remain unchanged.
