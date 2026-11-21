---
atom_family: SPEC
atom_id: AN-S-2367
structure:
  container:
    component: C16
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 12
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject Event selectors outside the canonical namespace

## Scope

The Journal-specific selector admission boundary.

## Claim

### Prose Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** reject every selector outside the
canonical Event namespace or with invalid pointer syntax before passing the
expression to CA-R-1850.

## Details

A valid Event selector is exactly `event:/` (only for full-Event query) or
`event:/` followed by a syntactically valid RFC6901 pointer. A selector outside
that namespace, a bad pointer escape or syntax, and dot-qualified traversal are
rejected locally. A valid pointer absent from an individual Event is passed to
CA-R-1850, where its comparison is false; explicit `null` remains a value.
SQL, code, grammar, boolean precedence, literal validity, and structural
comparison remain exclusively governed by CA-R-1850; this Requirement adds no
second expression grammar.
