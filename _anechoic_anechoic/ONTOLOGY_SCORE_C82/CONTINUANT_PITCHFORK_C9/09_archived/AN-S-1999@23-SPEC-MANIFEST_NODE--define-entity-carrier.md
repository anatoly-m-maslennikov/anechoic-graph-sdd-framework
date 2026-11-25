---
atom_family: SPEC
atom_id: AN-S-1999
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 23
  updated_at: "2026-11-25T20:21:08.574473+00:00"
---

## Summary

Define Entity/Carrier

## Claim scope

MODEL//ANECHOIC <+ Carrier

## Semantics

A Carrier holds or represents a Graph entity. A Markdown file can carry a Spec Atom. An Event Record represents an occurrence and its Carrier holds the record. A change to the Carrier format or file extension alone preserves the identity of the entity it holds.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Carrier:
    pass
```
