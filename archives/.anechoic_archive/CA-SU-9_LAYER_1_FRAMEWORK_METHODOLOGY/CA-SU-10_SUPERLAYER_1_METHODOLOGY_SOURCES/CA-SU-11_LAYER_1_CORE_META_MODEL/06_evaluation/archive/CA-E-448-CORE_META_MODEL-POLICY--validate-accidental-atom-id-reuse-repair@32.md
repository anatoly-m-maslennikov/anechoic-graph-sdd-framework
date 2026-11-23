---
subjects:
  active: ANECHOIC_MODEL <+ Atom.Header.ID
  passive:
  - ANECHOIC_MODEL <+ Atom.Header.ID
  - ANECHOIC_MODEL <+ Atom.Header.Role
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Atom.Local Scope Unit
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom.Header.Version
  - ANECHOIC_MODEL <+ Carrier.Canonical Address
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Execution Control <+ Decision Confidence
  - ANECHOIC_MODEL <+ Journal
version: 32
updated_at: 2026-11-02 18:35:20 +0400
relations:
  evaluation_for:
  - CA-M-276
atom_id: CA-E-448
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Active
tier: 5
role: Evaluation
form: Eval Policy
---
## Summary

Validate accidental Atom ID reuse repair

## Claim

### Prose Claim


Atom ID collision repairs.


the Evaluation **must** reject completion of an Atom ID collision repair under CA-M-276-CORE_META_MODEL-IMPLEMENTATION_METHOD--repair-accidental-atom-id-reuse **if** **any** of:

- the original owner was selected **without** sufficient recorded assignment evidence **or** the required Operator decision, **or** its valid Atom ID changed.
- a later accidental reuse retains the colliding ID, receives a previously used number, **or** receives an ID outside its Project prefix **and** Content Role sequence.
- an affected Claim, Content Role, Atom Scope, Claim Target Scope Unit, **or** textual Claim Scope changes beyond the approved identity-reference correction, a distinct Claim is lost **or** merged, **or** an unrelated identity changes.
- a prior Revision **or** historical Record is rewritten, history becomes unreachable, **or** the Work Journal lacks the exact mapping between the historical Carrier **and** its corrected identity.
- an affected current reference resolves ambiguously, remains unresolved, **or** resolves **to** a different intended Claim; an uncertain reference is rebound **without** the required Operator decision.
- legitimate same-Atom Revisions **or** derived copies are renumbered as accidental reuse, **or** lookup **or** compilation silently selects an identity winner.

the Evaluation **must** distinguish a paused collision awaiting an Operator decision from a completed repair. its checks **must** cover the verified-original-owner case, reversed Carrier discovery order, an unknown original owner, an ambiguous incoming reference, **and** legitimate same-Atom Revisions **or** derived copies.
