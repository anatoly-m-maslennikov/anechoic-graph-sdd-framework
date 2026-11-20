---
identity:
  atom_id: AN-S-2499
context:
  container:
    component: C9
  tier: 5
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-13T18:37:48.576277+00:00'
---
## Summary

Make Atom Claims clear and preserve their meaning

## Claim

### Prose Claim


Atom Claims.


**to** make an Atom Claim easy **to** understand, the Author **must** express **and** organize its content so the intended reader can identify what is claimed, what it concerns, **and** how its conditions **and** consequences fit together **without** guessing unstated connections.

## Details

### Meaning and context

- provide the context needed **to** interpret the Claim. reference existing governing definitions **and** authority rather than independently restating them.
- mention another Atom **in** prose **only when** an appropriate typed relation connects the Atoms. keep necessary execution bindings explicit; remove redundant context rather than invent a relation merely **to** retain a citation.
- render **every** prose Atom citation as the referenced Atom's complete filename **without** its `.md` extension **or** directory path, preserving **all** filename tokens **and** their exact spelling. direct machine references remain exact Atom IDs rather than citation labels, **and** the exact-revision reference rule continues **to** govern exact-revision metadata.
- choose familiar wording under the simpler-wording Method **without** losing precision, necessary distinctions, **or** exact canonical Terms.
- state conditions, alternatives, **and** relationships explicitly. preserve whether **all** conditions apply **or** **any** alternative suffices, including nested logical groups.

### Structure

- use short, direct statements. a simple Claim **may** remain a short paragraph; do **not** compress several points, conditions, **or** steps into one dense sentence.
- **when** several points share a subject **or** predicate, state that shared lead-in once **and** put the points **in** a list. preserve conjunctions, alternatives, conditions, **and** negation.
- use bullets for unordered points, conditions, **or** alternatives.
- use a numbered list for sequential steps **only** **when** the content establishes that sequence. numbering **must not** invent execution order **or** priority.
- make each Workflow Claim text self-sufficient: identify its Steps, calls or containing structure, applicable bindings, and routing conditions, next Steps or terminal outcomes. A flow table may carry this information, but is not mandatory when the text already supplies it. A Mermaid Scheme is a diagram-first visual summary and may repeat the text.

### Preservation

- preserve the complete Claim **and** its qualifications; easier wording **or** layout **must not** change its meaning.
- retain the Atom boundary under the composite-Claim boundary rule. one Claim does **not** require one sentence; paragraphs, bullets, **and** table rows do **not** determine the number of independently governed Claims.
- avoid redundant authoritative restatements in prose, lists and tables. A Mermaid Scheme may repeat its self-sufficient Claim text as a visual summary.
- preserve the exact spelling and case of canonical Terms and registered references.

readable layout alone is insufficient **when** the Claim still requires the reader **to** reconstruct missing context **or** logical connections.
