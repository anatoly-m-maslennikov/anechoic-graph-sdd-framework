---
atom_id: CA-M-442
ref_id: CA-M-442@6
container:
  scope_unit: CA-SU-11
role: Method
form: Implementation Method
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring
  dependencies:
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Atom.Content.Summary
  - ANECHOIC_MODEL <+ Atom.Content.Details
tier: 3
status: archived
version: 6
updated_at: '2026-11-13T18:21:42.441365+00:00'
carrier_destination:
  file:
    name: CA-M-442@6-CORE_META_MODEL-IMPLEMENTATION_METHOD--an-atom-s-content-expresses-one-scoped-contribution-with-a-faithful-summary-and-translations.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/099_archived
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

An Atom's content expresses one scoped contribution with a faithful Summary and Translations.

## Claim

### Prose Claim


authoring an Atom's prose primary contribution, its applicability, **and** its derived Summary. The same Claim may contain readable prose and an optional R-only nested Formal claim under the Claim definition.


**to** author one primary contribution **and** its derived Summary, an Author **must** use these authoring constraints:

- express **`=1`** coherent contribution whose full meaning is covered by one precise Summary under the applicable Role and Form. carry it under the primary contribution heading registered for the Content Role rather than imposing the literal heading Claim on **every** role.
- resolve **`=1`** Claim Target Scope Unit independently of ownership. select the current Scope Unit as the authoring default **or** an explicitly permitted different target; carry the resolved value under the target Scope Unit carrier definition. express applicability under the applicability carrier definition. for RMED, describe what the Claim applies **to**, including applicable conditions **and** exclusions, **in** Scope; do **not** merely repeat the carried current **or** target Scope Unit; those restrictions alone do **not** make the Atom Relational.
- keep Details within the primary contribution. for RMED, read the Claim within its Scope; Details **must not** change either. **if** supporting content reveals an incomplete **or** inaccurate contribution **or** applicability, revise the affected Scope **or** primary contribution explicitly **and** recheck agreement; do **not** hide the change **in** Details.
- for a new Atom, shorten the finalized primary contribution in the Summary. use plain wording that expresses the Claim’s meaning. preserve established principle names such as DRY **and** MECE instead of paraphrasing them. a familiar name **or** short instruction **may** be the Summary; do **not** force it into a declarative sentence. for RMED, summarize the Claim within its finalized Scope, **not** the Scope alone; do **not** substitute supporting Results **or** TLDR as the source.
- for an existing Atom, retain the established Summary **and** check its faithfulness; **if** the Summary needs changing, use a new Atom identity under the Atom identity rule.
- derive **every** Translation from the full corresponding source content, **not** the Summary.
