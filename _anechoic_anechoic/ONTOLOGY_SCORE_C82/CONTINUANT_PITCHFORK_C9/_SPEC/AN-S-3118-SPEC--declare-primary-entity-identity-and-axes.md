---
atom_family: SPEC
atom_id: AN-S-3118
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 10
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare Primary Entity identity and axes

## Claim

### Prose Claim

Declare Model meaning independently of Engine implementation. Author the Model with three Manifest forms: `manifest_node`, `manifest_property`, and `manifest_relation`. Use a `python anechoic-edsl` block when a declaration needs formal rules. Use Python classes and typed references for declarations and inheritance. Do not repeat declaration wrappers around each class. During migration, legacy `model_manifest` authoring remains valid.

A simple Node can be declared by its Concern. Use `node(Name, Base, ...)` when the Node needs explicit names or bases, or a class when it needs formal rules. Atom uses `identity = header.atom_id`. Assign inherited values in the class. For the Axiom, `container_type = value(fixed=Project)` fixes the target type. The inherited `IS_CONTAINED_BY` Relation requires one target.

A Property Manifest uses `bearer = ...` and typed references to declare its bearer, value type, and cardinality. Dependent Properties remain in their own carriers. A Property’s qualified path includes its bearer. Sibling Property names are unique.

Value format and cardinality are independent. Use Python types to distinguish Boolean, integer, floating-point, decimal, string, and datetime values. A format admits null only when declared. A literal value is data on its Property.

Count direct values separately from nested Properties. Uniqueness checks use their declared population and key tuple. A declared functional dependency requires equal dependent tuples for equal key tuples. An immutability check follows the same bearer across its admitted revisions. A class may assign `value(default=...)` for an overrideable fallback or `value(fixed=...)` for an invariant. Store a required Atom value chosen by default at its declared location. Leave absent optional overrides absent and retain explicit selections even when they equal an inherited value.

A Node class may declare `node.axes` as a mapping from an Axis name to an allowed value. Declare each Node Axis with `manifest_property`, `bearer = Axis`, `property.axis = True`, and `property.value.allowed`. Relation Axes use Relation as their bearer.

A scoped `NodeConstraints` class uses an explicit typed bearer and its existing Constraints scope.

A Relation Manifest declares the outbound endpoint schema and cardinality. Each endpoint specifies whether it accepts Model entities or instances. Apply the endpoint domains before Node constraints. Derive its inverse from the authored edge instead of authoring another edge. Inherited Properties apply to subtypes and subtype constraints can tighten or loosen them. Inheritance carries constraints and declaring sources. Instance values and Relation facts stay with their instances.

Property paths in identity and derivation rules are relative to the nearest Primary Entity. Nested Properties resolve through their declared bearers. Preserve these bindings and validation rules when migrating a declaration. Compare the compiled Model with its source and report unresolved or duplicate references.

Atom ID belongs directly to the YAML Header. The Model path is `Header.Atom ID`. State owns Status, Version, and Updated At. See AN-S-3160 for the native Header order. Ref ID is computed from Atom ID, Version, and Status. It adds `-draft` for a Draft.

## References

AN-T-2923, AN-T-2924, AN-S-149.
