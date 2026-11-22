---
atom_family: TKT
atom_id: AN-T-1956
container:
  component: C15
priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: 2026-11-10 21:28:00 +0400
---

## Summary

How should Engine topic addresses be admitted?

## Concern

Current Engine sources use ANECHOIC_STRUCTURE topic addresses, while the shared Declaration uses PROJECT STRUCTURE under ANECHOIC_MODEL. Some local Scope Delegations admit legacy Subject paths exactly. A topic can have the right meaning without an established exact canonical address or matching local admission.

## Details

Preserve the reviewed meanings and prepare source-bound topic Drafts. Before adoption, check each target against Current Declarations and the receiving Scope Delegation. Add only the missing local admissions; do not infer an equality between roots or replace operators globally.

The shared root bridge needs a Methodology decision outside this Engine source pass. Keep API, Workflow Run.Retry, History and UX Discovery and Navigation addresses explicit where an exact replacement remains unresolved. PROGRAMMATIC locally lists Provenance, but that admission does not by itself define a distinct topic or settle whether the shared Traceability topic should remain sufficient.

Proposed treatment: retain justified model and UX subjects, use the existing Engineering group where it fits, and review the bridge or missing declarations separately. Candidate topic Drafts do not establish new Current authority. Independent source review continues.

Blast radius: topic resolution and local permission checks for the changed Engine Drafts. No Claim rewrite, Scope tree change, source promotion, code change or runtime behavior is authorized by this Question.

## Resolution

Actual Current source checks pass: 363 RMEDO sources, 75 exact main subjects, zero missing or duplicate selected identities, and exact receiving Scope/Role/Form admissions. The rebuilt graph passed independent review. R3022 and the corrected local Delegations supply the source-bound addresses; no root equality or implicit descendant permission was inferred.

This closes source correction, not deployed query accessibility. C716 and implementation reader tasks retain runtime follow-up.
