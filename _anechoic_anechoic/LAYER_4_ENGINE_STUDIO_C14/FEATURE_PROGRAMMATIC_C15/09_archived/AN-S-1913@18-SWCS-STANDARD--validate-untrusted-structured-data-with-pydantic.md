---
atom_family: SPEC
atom_id: AN-S-1913
concern:
  subject: 'Module/(.Language := python)'
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content
  relation: is_contained_by
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: "archived"
  version: 18
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Validate untrusted structured data with Pydantic

## Semantics

The rule covers every structured Python record, including internal state and
test records. Pydantic dataclasses are permitted. Apply the committed Ruff
formatter and lint/complexity profile and the locked Mypy profile.

## Claim

### Formal Claim

```lean
namespace ProgrammaticPythonRecords

def conforms (structuredRecord : Bool) (usesPydantic : Bool) : Bool :=
  !structuredRecord || usesPydantic

end ProgrammaticPythonRecords
```

### Prose Claim

Use Pydantic for all structured Python models, including domain and state
records, configuration, IPC and persistence records, requests, results,
and test models. Keep validated Pydantic models throughout Python code.
Use the committed Ruff formatter and lint/complexity profile, including
F401, B006 and configured C901 limits. Run the locked Mypy profile against
its declared targets.

## Details

### Procedure

1. Declare field types and constraints before custom validators.
2. Validate raw data strictly at admission. Permit coercion only for a
   declared interoperability need. Make the conversion observable.
3. Reject undeclared fields in closed contracts.
4. Report structured diagnostics when validation fails. Pass the validated
   model internally without repeating validation solely to pass it.

### Failure or stop

Static rejects identifiable unmodeled records. Report possible dictionary
records for review. Convert confirmed records to Pydantic and retain
ordinary maps. Use admission tests for dynamically constructed records.

Refuse admission when the boundary is undeclared, coercion is silent, or
a closed contract accepts extra fields.

### Sources

- [Pydantic: models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic: strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [Pydantic: model configuration](https://docs.pydantic.dev/latest/concepts/config/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
