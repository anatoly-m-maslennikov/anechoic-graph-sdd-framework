---
atom_family: SPEC
atom_id: AN-S-3092
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "draft"
  version: 3
  updated_at: "2026-11-25T11:10:28.020285+00:00"
---

## Summary

Declare Model

## Semantics

A Model defines the kinds of entities a domain admits and the rules that
apply to their instances.

The Graph Model defines abstract entities and their relationships. The
Carrier Model defines the files and folders that represent Graph entities.
Each has its own root.

Main axes organize the Model tree through containment, specialization, and
Property ownership. Secondary axes apply across branches. Each secondary
axis defines its allowed values. For example, Temporal Kind has the values
Continuant and Occurrent.

## Claim scope

MODEL//ANECHOIC <+ Model

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Model:
    pass
```
