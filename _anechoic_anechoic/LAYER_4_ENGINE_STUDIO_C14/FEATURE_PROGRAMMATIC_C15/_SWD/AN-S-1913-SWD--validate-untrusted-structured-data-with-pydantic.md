---
atom_family: SPEC
atom_id: AN-S-1913
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 15
  updated_at: '2026-11-24T18:58:19.252479+00:00'
---

## Summary

Validate untrusted structured data with Pydantic

## Claim

### Prose Claim

Use Pydantic for all structured Python models, including domain and state
records, configuration, IPC and persistence records, requests, results,
and test models. Keep validated Pydantic models throughout Python code.

## Details

### Procedure

1. Declare field types and constraints before custom validators.
2. Validate raw data strictly at admission. Permit coercion only for a
   declared interoperability need. Make the conversion observable.
3. Reject undeclared fields in closed contracts.
4. Report structured diagnostics when validation fails. Pass the validated
   model internally without repeating validation solely to pass it.

### Failure or stop

Refuse admission when the boundary is undeclared, coercion is silent, or
a closed contract accepts extra fields.

### Sources

- [Pydantic: models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic: strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [Pydantic: model configuration](https://docs.pydantic.dev/latest/concepts/config/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
