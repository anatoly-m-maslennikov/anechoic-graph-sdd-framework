---
atom_family: SPEC
atom_id: AN-S-3118
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T13:19:17.551675+00:00"
---

## Summary

Limit Primary Entity Manifests to identity and classification

## Claim

### Prose Claim

Author the Model with three Manifest forms: `manifest_node`, `manifest_property`, and `manifest_relation`. Each has one `python anechoic-edsl` block. Use Python classes and typed references for declarations and inheritance. Do not repeat declaration wrappers around each class. During migration, legacy `model_manifest` authoring remains valid.

A Node Manifest declares an ordinary class with its bases or `pass`. Atom uses `identity = header.atom_id`. Assign inherited values in the class. For the Axiom, `container_type = value(fixed=Project)` fixes the target type. The inherited `IS_CONTAINED_BY` Relation requires one target.

A Property Manifest uses `bearer = ...` and typed references to declare its bearer, value type, and cardinality. Dependent Properties remain in their own carriers. A class may assign `value(default=...)` for an overrideable fallback or `value(fixed=...)` for an invariant.

A Node class may declare `classifications` as a mapping from an axis name to an allowed value. Declare Model classification domains with `manifest_property`, `bearer = Classification`, `classification = True`, and `allowed_values`. Relation classification axes use the separate existing `manifest_property` form with Relation as bearer.

A scoped `NodeConstraints` class uses an explicit typed bearer and its existing Constraints scope.

A Relation Manifest declares the outbound endpoint schema and cardinality. Derive its inverse from the authored edge instead of authoring another edge. Inherited Properties apply to subtypes and subtype constraints can tighten or loosen them.

Property paths in identity and derivation rules are relative to the nearest Primary Entity. Nested Properties resolve through their declared bearers. Preserve these bindings and validation rules when migrating a declaration. Compare the compiled Model with its source and report unresolved or duplicate references.

Atom ID belongs directly to the YAML Header. The Model path is `Header.Atom ID`. State owns Status, Version, and Updated At. See AN-S-3160 for the native Header order. Ref ID is computed from Atom ID, Version, and Status. It adds `-draft` for a Draft.

## References

AN-T-2923, AN-T-2924, AN-S-149.
