---
atom_family: SPEC
atom_id: AN-S-276
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C37
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 29
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Generate the Project Scope Unit Graph from Configuration Authority

# Generate the Project Scope Unit Graph from Configuration Authority

**to** generate the Project Scope Unit Graph **and** Sources Projections:

- Use the Project Structure authority in AN-S-274.
- use Project Settings for Project identity **and** Framework Instance Settings for selected framework behavior, under their governing authority.
- preserve the distinction between accepted declarations, Atom Claims, Directory Carrier observations, **and** Journal evidence.
- Derive deterministic views from the selected source revisions. Leave
  accepted declarations unchanged and apply AN-S-274 to coverage.
- Report incomplete reads as incomplete coverage.
