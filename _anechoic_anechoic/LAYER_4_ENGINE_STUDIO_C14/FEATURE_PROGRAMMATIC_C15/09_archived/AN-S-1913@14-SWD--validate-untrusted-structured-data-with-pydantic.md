---
atom_family: SPEC
atom_id: AN-S-1913
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 14
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Validate untrusted structured data with Pydantic

## Claim



### Prose Claim
use Pydantic **when** untrusted structured data crosses an admitted Python
boundary. validate once at the boundary **and** pass accepted typed values into
the deterministic core **without** making Pydantic the universal internal model.

## Details


### Applicable when

apply **to** an admitted CLI payload, Hook event, configuration carrier, Journal
record, protocol message, **or** external adapter whose invalid structure could
hide a contract defect.

### Procedure

1. define the bounded input model with field types **and** constraints **before**
   custom validators.
2. use strict validation **when** coercion could hide a defect; admit lax conversion
   **only** for a declared interoperability need **and** make it observable.
3. reject undeclared extra fields for closed machine contracts.
4. return structured validation diagnostics **and** pass the accepted typed value
   **to** the deterministic core.
5. add Pydantic as a runtime dependency **only** **where** validation **and** schema value
   justify its dependency cost.

### Outcome

untrusted structured inputs become explicit typed values at one boundary while
the internal model remains independent of the validation library.

### Failure or stop

stop admission **when** the boundary is **not** declared, coercion is silent, extra
fields escape a closed contract, **or** the dependency has no bounded benefit.

### Sources

- [Pydantic: models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic: strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [Pydantic: model configuration](https://docs.pydantic.dev/latest/concepts/config/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
