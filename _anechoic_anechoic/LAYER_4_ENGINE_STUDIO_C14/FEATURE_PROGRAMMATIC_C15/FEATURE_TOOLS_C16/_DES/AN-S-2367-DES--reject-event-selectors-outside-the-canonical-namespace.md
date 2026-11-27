---
atom_family: SPEC
atom_id: AN-S-2367
concern:
  subject: "Event Record"
  path: "Model/Graph/Node//Artifact//SSOT//Recorded"
  relation: "is_narrower_than"
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: active
  version: 14
  updated_at: "2026-11-27T16:29:34.309627+00:00"
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

Use the namespace and pointer rules in AN-S-2360. Resolve absent values
and explicit null under AN-S-2366. The root selector is reserved for a
full-Event query. Apply CA-R-1850 for expression evaluation.
