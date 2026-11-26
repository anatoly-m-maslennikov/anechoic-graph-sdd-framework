---
atom_family: SPEC
atom_id: AN-S-4036
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define Project Implementation

## Claim

Project Implementation is the single root Package of a Project's implementation. It has no enclosing Package. It realizes RMED and may be directly edited; it is not automatically a Projection merely because it realizes a specification.

### Formal claim

```text
Package/Project Implementation
Project Implementation > @(Package)
```

## Semantics

Implementation is the section heading for this model area. Project Implementation is the root Package kind, rather than a part of a second Implementation kind. Modules execute on their language engine; Prompts execute on an LLM AI Agent engine; Assets are non-executable content. Logical parts remain distinct from their Carriers and from live Runtimes.

## Details

CA-A-1259 records this decision. Numeric identity is pending; no Current source promotion is claimed. CA-A-1266 places Documentation directly in Package, separately from runtime-required Asset. Former Resources members are classified as Assets, Prompts or Documentation; Current migration remains pending.
