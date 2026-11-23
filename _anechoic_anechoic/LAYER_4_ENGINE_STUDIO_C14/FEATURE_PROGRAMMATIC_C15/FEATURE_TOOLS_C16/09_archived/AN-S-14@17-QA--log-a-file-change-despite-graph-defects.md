---
atom_family: SPEC
atom_id: AN-S-14
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Log a file change despite graph defects

# Log a file change despite graph defects

## Claim checked

COMMIT_CONTEXT records an observed file action **without** requiring the surrounding Project graph **or** the changed Carrier **to** conform **to** Applicable Methodology.

## Cases

1. change an Atom while unrelated Carriers share an identity **and** one authored relation names a mismatched **or** missing target.
2. change a Carrier with a broken Atom filename, a legacy ID, invalid lifecycle placement, **or** malformed authored properties.
3. repeat capture for the same observation **without** running a Project-conformance Evaluation.

## Acceptance

- capture returns the actual file action, exact observable path, **and** its observed evidence **without** mutation.
- use unambiguous available classification **and** relation bindings; retain unknown **or** conflicting values as such. do **not** invent a conforming Atom ID, Version, target, **or** graph state.
- preserve a recordable native Carrier observation **when** optional Atom classification fails.
- already available diagnostics **may** accompany the context. their absence **must not** require a conformance scan **or** block the Journal.
- the returned context does **not** assert that the Project passed an Evaluation.

## Failure disposition

reject the logger Implementation **if** it blocks recordable facts on Project-conformance defects, silently repairs observed values, requires a conformance scan, **or** mutates the Project during capture.
