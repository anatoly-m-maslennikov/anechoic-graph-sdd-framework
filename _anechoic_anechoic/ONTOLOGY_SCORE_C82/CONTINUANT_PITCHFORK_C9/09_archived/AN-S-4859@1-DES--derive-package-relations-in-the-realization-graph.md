---
atom_family: SPEC
atom_id: AN-S-4859
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-24T22:03:05+00:00'
---

## Summary

Derive Package relations in the Realization Graph

## Claim

### Prose Claim

Both endpoints A and B are Package instances identified under AN-S-3159. The endpoint rules of AN-S-2611 apply. Explicit–derived pairs have one authored Direct relation and a computed inverse. Derived–derived pairs compute both directions from the same inputs, as in these Realization Graph relations. Retain a trace to the source. Unresolved bindings emit no Package edge.

| A to B | B to A | Classification of both directions | Evidence |
| --- | --- | --- | --- |
| IMPORTS | IS_IMPORTED_BY | Derived | A resolved import occurrence and immediate ownership of its endpoints, per AN-S-3085. Intra-Package imports remain visible. |
| CONTAINS | CONTAINED_BY | Derived | Immediate admitted Package structure. |
| IS_SIBLING_OF | IS_SIBLING_OF | Derived | Distinct Packages have the same immediate structural parent. |
| IS_UPSTREAM_LAYER_FOR | IS_DOWNSTREAM_LAYER_FOR | Derived | Relative layer order within the same ordered sibling group. |
| CALLS_API_OF | HAS_API_CALLER | Derived | A resolved client in A calls an operation owned by B. |
| STARTS_PROCESS_OF | HAS_PROCESS_STARTED_BY | Derived | A launch site owned by A resolves to an entry point owned by B. |
| READS_STATE_OWNED_BY | HAS_STATE_READER | Derived | A resolved resource read by A and its designated owner B. |
| WRITES_STATE_OWNED_BY | HAS_STATE_WRITER | Derived | A resolved resource written by A and its designated owner B. |
| PUBLISHES_EVENTS_CONSUMED_BY | CONSUMES_EVENTS_PUBLISHED_BY | Derived | Resolved publisher and consumer bindings to the same channel and event type, owned by A and B respectively. |

IS_SIBLING_OF is symmetric: use the same name in both directions and emit no self-pairs. Graph-scoped Package containment is computed from the immediate admitted structure; AN-S-2715 defines its meaning.
