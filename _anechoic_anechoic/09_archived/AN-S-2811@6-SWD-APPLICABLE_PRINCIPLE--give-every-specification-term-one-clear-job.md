---
atom_family: SPEC
atom_id: AN-S-2811
concern:
  subject: Distinct meanings for Spec terms
  path: Design Foundations/Information and complexity
  relation: is_contained_by
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-27T13:06:15.070796+00:00"
relations:
  SERVES:
  - AN-S-1233
---
**P32**

## Summary

Give every specification term one clear job

## Claim

### Prose Claim

Name the exact thing or relationship you mean. If a keyword can mean several different things in the same specification, replace it with distinct names. A person, an AI Agent, and a tool should not have to guess which meaning applies.

## Details

### Examples

A specification uses “Component” for an owned part and “Module” for a unit of code.
