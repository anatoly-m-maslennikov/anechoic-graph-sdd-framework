---
identity:
  atom_id: AN-S-2270
context:
  container:
    component: C15
  tier: 3
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-13T16:30:09.035081+00:00'
---
## Summary

Reuse built-in Python capabilities

## Claim

### Prose Claim

Use built-in Python capabilities and the standard library when they satisfy the applicable requirements. Reuse an existing Project dependency when it covers a gap in the standard library.

For the Model build and validation:

- Use `dataclasses` and ordinary class inheritance for Model classes and fields.
- Use `graphlib.TopologicalSorter` to order class definitions and detect inheritance cycles. Verify that each referenced parent is declared.
- Use `ast.parse()` to inspect Python Formal Claims and `compile()` to check the assembled Python before testing its import.
- Use the Project's existing Pydantic dependency in strict mode for field validation before writing. Read field types, allowed values, and collection bounds from the Model Declarations.
