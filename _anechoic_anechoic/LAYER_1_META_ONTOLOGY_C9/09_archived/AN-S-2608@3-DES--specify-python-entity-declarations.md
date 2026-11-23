---
atom_family: SPEC
atom_id: AN-S-2608
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T01:06:17.792126+00:00'
---
## Summary

Specify Python entity declarations

## Claim

### Prose Claim

- Declare each named Model Entity, Property, or instance with `declare_entity`.
- For a narrower kind, pass its Python class as `entity_class`. A singleton uses an explicit instance population cardinality in the Project. Declare the parent using ordinary Python class syntax. Derive the narrower Model address from that parent and the declared name.
- Use `qualification_property_path` when the declared name is an allowed Property value. A Form class extends its Role class.
- For a Property, pass `entity_name`, `relation_name="IS_PROPERTY_OF"`, and its bearer as `base_path`. Declare Property occurrence and direct values separately. Use `dependent_property_cardinality` to count immediate dependent Properties. Use `dependent_property_value_cardinality` with `dependent_property_value_format` to constrain the direct values of each immediate dependent Property.
- Put Model and instance Relation permissions in separate declaration fields.
- For a conditional instance rule, define a named Python function with a Model-typed parameter and a `bool` return. Pass it to `declare_entity` as `instance_check`.

## Details

The Core Model resolver binds Python class imports to declared Model addresses. A Claim supplies its own imports and declaration arguments. Primary Entities are Python classes. Properties become typed data fields on their bearers. Use standard dataclass field machinery when a class needs a data representation. Keep each inherited field’s Property Declaration on its original bearer. An Entity's local rule overrides an inherited rule for the same Property or Relation. A local MODEL override explicitly identifies the inherited rule it replaces.

- Register each class by its full qualified Model address. Each Role-scoped Form has its own class identity.
- Represent Properties as typed dataclass fields on their declared bearer. Assemble nested records from their Property Declarations and retain field provenance.
