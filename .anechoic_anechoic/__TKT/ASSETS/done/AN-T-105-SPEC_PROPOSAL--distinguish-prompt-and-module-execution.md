---
identity:
  atom_id: AN-T-105
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: done
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Distinguish Prompt and Module execution

## Decision

Implementation > Package > Prompt. A Prompt is executable instructions for an LLM AI Agent engine. A Module is executable by its language engine, through compilation or interpretation as applicable. Prompt and Module are logical Implementation parts; their File or other Carriers are representations, not execution engines. Asset covers non-executable Implementation content; Prompt is not classified as Asset merely because its stored text file is not executable by the operating system. This refines the previous instructional-purpose definition without introducing another Runtime kind or Relation Type.

## State

Updates review Drafts only. Current sources, code and runtime remain unchanged.
