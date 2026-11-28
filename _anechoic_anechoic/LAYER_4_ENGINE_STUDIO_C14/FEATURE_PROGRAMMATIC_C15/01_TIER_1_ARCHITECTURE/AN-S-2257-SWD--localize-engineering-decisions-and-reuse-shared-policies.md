---
atom_family: SPEC
atom_id: AN-S-2257
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: "active"
  version: 3
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---
## Summary

Localize engineering decisions and reuse shared policies

## Claim scope

Every new or changed PROGRAMMATIC implementation decision represented by an
implemented RMED Atom, across Requirements, Methods, Evaluations and Deliveries
and their descendant Scope Units.

## Claim

### Prose Claim

Localize each implemented RMED engineering decision in one owning Module or one cohesive Package when practical. For R and D, prefer one cohesive Module and as few code units as practical, ideally one. Preserve complete realization of each Claim and truthful many-to-many implementation relations.

Split implementation across Modules only at a genuine responsibility, lifecycle, effect, interface, data, or security boundary. Record the concrete reason. Preserve correctness and cohesion. Avoid scattering or duplicating logic, inflating a Module, or omitting obligations to meet a count.

Implement each cross-cutting policy once at a shared canonical boundary, such as a decorator. Apply it everywhere the policy applies. Count copied policy logic as an implementation site during review.

## Details

For R, count the implementation of Claim-specific meaning, behavior or enforcement. For D, count the implementation of representation, serialization, storage or placement. Include non-executable implementation when it realizes the Claim.

Use code units such as functions or classes to assess implementation granularity.

Assign ownership to the Modules or Packages that realize the Claim. Count a caller, adapter, router, orchestration layer, dependency or facade only when it materially implements part of the Claim. A test owns an Evaluation when it implements its check, fixture or verification behavior.

Record the actual owners and exact revisions under AN-S-2259 and AN-S-2256. Leave unimplemented Atoms without implementation targets.

This Method sets an organization preference. Existing approval and test policies govern their own scope.
