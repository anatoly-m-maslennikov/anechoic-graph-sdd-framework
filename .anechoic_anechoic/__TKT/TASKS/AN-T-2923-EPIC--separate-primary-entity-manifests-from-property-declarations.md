---
identity:
  atom_id: AN-T-2923
context:
  container:
    component: C00
  tier: 3
  template: epic
state:
  status: active
  version: 2
  updated_at: '2026-11-20T16:57:42.524056+00:00'
---
## Summary

Separate primary entity Manifests from Property declarations

## Objective

Make identity and Primary/Property classification explicit in the Model.
Declare Properties separately and compile them into the types and
validators used by implementation.

## Work

1. AN-T-2924 defines the ontology and whitelist.
2. AN-T-2925 updates Manifest Compiler and Model Host after the ontology is set.
3. AN-T-2926 applies the approved layout to the Project's Manifests.

## Carrier format follow-up

Atom source is the YAML Header plus Markdown Content. Filename, location,
Destination, and Ref ID are derived. The Header stores Atom Family first
and the full Atom ID second. It then carries optional Concern, Structure,
Context, optional Relations, and State.

Concern has subject, path, and relation. Structure carries Container and
SPEC Tier. Context carries Template and SPEC Lens. TKT can author Priority.
A Package Spec identifies its Package in its Formal Claim.

Proceed in this order:

1. AN-T-2929 defines the Carrier Model and validators.
2. AN-T-2930 updates tools after the Model.
3. AN-T-2931 recovers authored data from Git and migrates Carriers after the tools.

Keep the original mappings and exact revisions. Recover authored values
against their original Git evidence. Preserve any ambiguous or held data
for review, without inferring authored values from filename or location.

## Reference

AN-T-2791, Manifest Runtime.
