---
atom_family: SPEC
atom_id: AN-S-1479
container:
  component: C58
tier: 1
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 31
  updated_at: "2026-11-25T22:39:51.170742+00:00"
---
## Summary

Record every Projection rebuild in a Journal

## Claim

### Prose Claim


Business Projection rebuild attempts. Technical read-only queries and maintenance of rebuildable query indexes are runtime activities, not Projection rebuild attempts under this Rule.


For each business Projection rebuild attempt, record one append-only Journal Action from its start through one terminal outcome. Bind the target Projection, exact source Atom revisions and Journal records, generator, and configuration. For a published result, record its exact revision, Updated At, output Carrier reference, and content digest. Record the generation method as provenance. Verify currentness against the Projection specification and its sources.

## Details

technical read-only queries and maintenance of rebuildable query indexes report normal output through runtime stdout and failures through runtime stderr. these activities create no Journal provenance obligation under this Rule.
