---
atom_family: SPEC
atom_id: AN-S-1999
concern:
  subject: Carrier
  path: Model
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 27
  updated_at: '2026-11-26T16:50:11.585137+00:00'
---

## Summary

Define Entity/Carrier

## Semantics

A Carrier holds or represents a Graph entity. A Markdown file can carry a Spec Atom. An Event Record represents an occurrence and its Carrier holds the record. A change to the Carrier format or file extension alone preserves the identity of the entity it holds. Each binding identifies the entity actually represented, including the exact revision for an Archive. A Carrier retains its own identity when an entity refers to it through a binding. An authoritative representation preserves the carried revision’s content.

