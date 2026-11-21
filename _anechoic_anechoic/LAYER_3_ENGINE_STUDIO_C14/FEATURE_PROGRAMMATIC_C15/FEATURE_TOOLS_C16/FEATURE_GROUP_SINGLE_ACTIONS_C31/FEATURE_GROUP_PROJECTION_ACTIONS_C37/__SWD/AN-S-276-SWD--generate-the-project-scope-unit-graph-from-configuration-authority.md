---
atom_family: SPEC
atom_id: AN-S-276
structure:
  container:
    component: C37
  tier: 2
context:
  lens: SWD
state:
  status: active
  version: 27
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Generate the Project Scope Unit Graph from Configuration Authority

# Generate the Project Scope Unit Graph from Configuration Authority

**to** generate the Project Scope Unit Graph **and** Sources Projections:

- use the owning Project's authoritative Project Structure Artifact as the sole source of accepted Scope Unit declarations **and** concrete bindings.
- use Project Settings for Project identity **and** Framework Instance Settings for selected framework behavior, under their governing authority.
- preserve the distinction between accepted declarations, Atom Claims, Directory Carrier observations, **and** Journal evidence.
- derive the generated views deterministically from the selected source revisions **without** using previous generated views as authority **or** writing accepted declarations.
- keep Goal coverage, folder materialization, undeclared folders, **and** declaration mismatches visible as separate observations.
- **if** the required authoritative input is missing, invalid, **or** cannot be read completely, report incomplete coverage **and** do **not** claim a complete accepted Project Structure.
