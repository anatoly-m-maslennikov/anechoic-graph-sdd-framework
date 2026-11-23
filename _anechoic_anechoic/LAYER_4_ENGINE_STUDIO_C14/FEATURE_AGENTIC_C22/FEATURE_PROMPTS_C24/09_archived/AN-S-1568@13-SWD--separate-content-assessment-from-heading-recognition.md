---
atom_family: SPEC
atom_id: AN-S-1568
container:
  component: C24
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Separate content assessment from heading recognition

# Summary

Separate content assessment from heading recognition

## Scope

authoring the content-review instructions of the RMED review prompts.

## Claim

**to** implement local content assessment, use semantic reading of the complete carried text for content judgments **and** structural parsing for Property conformance, keeping the two judgments separate.

## Details

- instructions request actual quoted passages **and** an explanation of their semantic function, including applicability, contribution, supporting detail, **or** Summary.
- a missing heading is evidence of a Carrier defect; it is **not** evidence that readable content cannot be assessed. a semantic interpretation does **not** declare a missing Property section present.
- instructions distinguish independently replaceable Claims from clauses, examples, **or** conditions of the same Claim. they preserve useful content **when** proposing a correction.
- unresolved meaning **or** genuinely unavailable evidence is stated precisely for the affected check. a generic layout failure is insufficient justification for skipping readable content.
