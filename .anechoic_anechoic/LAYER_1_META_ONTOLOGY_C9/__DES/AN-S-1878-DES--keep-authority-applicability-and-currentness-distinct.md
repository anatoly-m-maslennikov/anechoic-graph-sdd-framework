---
atom_family: SPEC
atom_id: AN-S-1878
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 26
  updated_at: 2026-11-11 18:46:16 +0400
---
## Summary
Keep Authority, Applicability, and Currentness distinct

## Claim

### Prose Claim


an Artifact's Authority, Applicability, and Currentness Properties.


an Artifact's Authority, Applicability, **and** Currentness **must** remain distinct Properties under CA-R-1499, CA-R-1500, **and** CA-R-1501.

- an authoritative Artifact **may** be inapplicable **to** a given context.
- an applicable historical Revision **may** no longer be current.
- a current Projection **may** accurately report state **without** possessing semantic authority.

## Details

acceptance, provenance, Implementation, evidence, **and** Evaluation do **not** silently establish **any** of these Properties. precedence **and** conflict resolution select among **otherwise** authoritative **and** applicable Claims; they do **not** merge these Properties. the owning Requirement, Method, Evaluation, Delivery, **and** Operations Atoms govern how these Properties are resolved **and** reported through derived views.
