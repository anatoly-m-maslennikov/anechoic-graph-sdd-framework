---
atom_family: SPEC
atom_id: AN-S-4040
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

Define Eval Package

## Claim

An Eval Package is a Package for evaluation implementation. It can contain executable Modules and executable Prompts, together with the Assets needed by those evaluations. Module-based tests are one supported evaluation mechanism; evaluations are not restricted to tests written as code. The common Package structure also applies.

### Formal claim

```text
Package/Eval Package
Eval Package > @(Module)
Eval Package > @(Prompt)
```

## Semantics

An Eval Package is still a Package; it is not a new executable kind. Modules run on their language engine and Prompts on an LLM AI Agent engine. Assets are their non-executable inputs, distinct from their Carriers.

## Details

