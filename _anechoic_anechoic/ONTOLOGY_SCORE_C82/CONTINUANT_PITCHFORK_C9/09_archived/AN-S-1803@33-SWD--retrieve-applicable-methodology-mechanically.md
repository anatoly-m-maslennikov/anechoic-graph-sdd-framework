---
atom_family: SPEC
atom_id: AN-S-1803
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-25T22:11:28.045556+00:00"
---
## Summary

Retrieve Applicable Methodology Mechanically

## Claim

### Prose Claim


Applicable Methodology retrieval for one Subject **or** Workflow query.


**to** retrieve Applicable Methodology for one Subject **or** Workflow query, the Retriever **must** derive GOVERNS **and** DEPENDS_ON indexes on demand from projected Atom Subjects, select matching GOVERNS paths, add DEPENDS_ON authority **only** through transitive prerequisite closure, retain Applicable Methodology membership order, make no inference, **and** return no Atom **if** no matching GOVERNS path exists.
