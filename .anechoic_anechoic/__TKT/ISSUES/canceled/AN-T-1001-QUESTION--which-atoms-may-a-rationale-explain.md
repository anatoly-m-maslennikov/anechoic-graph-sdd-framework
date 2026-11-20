---
atom_family: TKT
atom_id: AN-T-1001
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: "canceled"
  version: 4
  updated_at: "2026-11-20T20:34:46.067797+00:00"
---
## Summary

Which Atoms may a Rationale explain?

# Which Atoms may a Rationale explain?

does the admitted Rationale target domain remain RMED **or** include Operations, **and** which existing authority owns its creation gate **and** Carrier exclusions?

## Evidence

META-REQU-119 requires prior existence of explained specification Atoms, a forward relation, no embedded Rationale **or** persisted backlink, **and** no change **to** normative meaning through explanation. R-1016 explicitly admits R, M, E, **and** D targets for `rationale_for`; R-1337 **and** GOV-REQU-750 already establish non-normative explanation. newer Operations definitions do **not**, by themselves, amend that Relation Kind's endpoint domain.

## Principle check

CA-M-002 favors reuse of R-1016 **and** Analysis authority; CA-M-006 requires the endpoint domain **and** callers **to** agree; CA-R-1490 protects the prior-existence gate **and** Carrier exclusions. the expanded `evaluation_for` domain is **not** authority **to** expand `rationale_for` by analogy. an absent backlink **and** the ban on embedding an entire Rationale are **not** the same condition.

## Disposition

preserve META-REQU-119 **and** R-1016 until the target domain is explicit **and** unique Carrier obligations have a confirmed owner. do **not** infer Operations permission, erase the creation gate, **or** move the entire mixed Claim into O merely because it mentions creation.
