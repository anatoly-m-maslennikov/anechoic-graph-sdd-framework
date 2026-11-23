---
atom_family: SPEC
atom_id: AN-S-2888
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-09-27 16:46:44 +0400
---
## Summary

Make Atom Claims easy to understand

# Make Atom Claims easy to understand

**to** make an Atom Claim easy **to** understand, the Author **must** express **and** organize its content so the intended reader can identify what is claimed, what it concerns, **and** how its conditions **and** consequences fit together **without** guessing unstated connections.

## Meaning and context

- provide the context needed **to** interpret the Claim. reference existing governing definitions **and** authority rather than independently restating them.
- render **every** prose Atom citation as its exact Atom ID **and** source-faithful Summary, for example `CA-R-366 — Reference exact Atom Revisions by version and time`, **not** a filename. direct machine references remain exact Atom IDs rather than citation labels, **and** `CA-R-366 — Reference exact Atom Revisions by version and time` continues **to** govern exact-revision metadata.
- choose familiar wording under `CA-M-294 — Use simpler words without losing meaning` **without** losing precision, necessary distinctions, **or** exact canonical Terms.
- state conditions, alternatives, **and** relationships explicitly. preserve whether **all** conditions apply **or** **any** alternative suffices, including nested logical groups.

## Structure

- use short, direct statements. a simple Claim **may** remain a short paragraph; do **not** compress several points, conditions, **or** steps into one dense sentence.
- use bullets for unordered points, conditions, **or** alternatives.
- use a numbered list for sequential steps **only** **when** the content establishes that sequence. numbering **must not** invent execution order **or** priority.
- use a flow table for a Workflow with branches **or** loops. identify **every** Step, its **`=1`** Action reference **and** parameter/input bindings, **and** the typed Relation, result condition, **and** next Step **or** terminal outcome for **every** transition under `CA-R-1508 — Define Workflow`.

## Preservation

- preserve the complete Claim **and** its qualifications; easier wording **or** layout **must not** change its meaning.
- retain the Atom boundary under `CA-R-1270 — Permit One Composite Claim as One Authority Unit`. one Claim does **not** require one sentence; paragraphs, bullets, **and** table rows do **not** determine the number of independently governed Claims.
- express authoritative content once rather than repeating the same Claim **in** prose **and** a list **or** table.
- apply the Term **and** CCE Operator rendering Method under `CA-M-229 — Render Governed Terms and CCE Operators Distinctly` throughout.

readable layout alone is insufficient **when** the Claim still requires the reader **to** reconstruct missing context **or** logical connections.
