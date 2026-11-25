---
atom_family: SPEC
atom_id: AN-S-1479
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 30
  updated_at: "2026-11-25T21:03:28.293068+00:00"
---
## Summary

Record every Projection rebuild in a Journal

## Claim

### Prose Claim


Business Projection rebuild attempts. Technical read-only queries and maintenance of rebuildable query indexes are runtime activities, not Projection rebuild attempts under this Rule.


**every** business Projection rebuild attempt **must** produce append-only Journal provenance from its start through **`=1`** terminal outcome, binding the target Projection, exact source Atom revisions **and** Journal records, generator, configuration, **and** produced revision **when** successful. Programmatic generation **and** LLM generation are provenance facts **only**; the two generation forms grant the Projection no authority.

## Details

technical read-only queries and maintenance of rebuildable query indexes report normal output through runtime stdout and failures through runtime stderr. these activities create no Journal provenance obligation under this Rule.
