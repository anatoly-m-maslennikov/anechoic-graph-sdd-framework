---
atom_family: SPEC
atom_id: AN-S-192
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Extract one Extension candidate from Project Adaptation

# Extract one Extension candidate from Project Adaptation

## Applicable when

use this Method **when** an operator selects reusable Project Adaptation authority for extraction as one Extension candidate.

## Procedure

1. seal the operator-selected adaptation Atoms **and** resolve their direct dependency closure across current active authority.
2. traverse declared required dependencies **to** the complete closure **and** preserve **every** selected **and** transitively required source Atom reference exactly.
3. reject the extraction **when** **any** required dependency is absent, ambiguous, **or** unresolved; do **not** omit it **or** infer a replacement.
4. assign the candidate its own stable identity **and** preserve the exact selected membership, transitive closure, source revisions, **and** frontier digest.
5. emit the bounded candidate **without** modifying its source Project Adaptation authority.

## Outcome

one independently identified Extension candidate **contains** the selected Project Adaptation authority **and** its complete attributable required dependency closure.

## Failure or stop

stop on unresolved required dependencies, stale source revisions, ambiguous closure, **or** a candidate boundary that cannot be attributed exactly.
