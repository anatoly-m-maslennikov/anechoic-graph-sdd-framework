---
atom_family: SPEC
atom_id: AN-S-3092
concern:
  subject: Model
  path: ANECHOIC
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 5
  updated_at: '2026-11-26T18:38:58.296902+00:00'
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
axis defines its allowed values. For example, Temporality has the values
Continuant and Occurrent.

