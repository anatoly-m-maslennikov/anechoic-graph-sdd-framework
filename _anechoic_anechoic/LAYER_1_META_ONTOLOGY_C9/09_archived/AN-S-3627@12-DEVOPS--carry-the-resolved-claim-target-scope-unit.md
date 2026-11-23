---
atom_family: SPEC
atom_id: AN-S-3627
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 12
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Carry the resolved Claim Target Scope Unit

# Summary

Carry the resolved Claim Target Scope Unit

## Scope

the frontmatter representation of an Atom's resolved Claim Target Scope Unit.

## Claim

a Markdown Atom Carrier **must** carry its resolved Claim Target Scope Unit **in** frontmatter, including a Current-scope Atom whose target is its own Scope Unit.

- choose the current Scope Unit as the default during authoring, **not** by relying on the file's later location.
- a carried target equal **to** the current Scope Unit does **not** make the Atom Relational. a different target still requires the applicable Relational Atom admission.
- Claim Scope restrictions use the body sections under CA-D-495-CORE_META_MODEL-CORE-DELIVERY--carry-applicability-in-the-registered-body-sections; the RMED Scope section does **not** replace **or** duplicate `claim_target_scope_unit`.

- encode this Property as the top-level nonempty YAML string `claim_target_scope_unit`, resolving **to** **=1** registered Scope Unit. null, lists, **and** a duplicated `claim_scope` field are **not** this encoding.
- an external Project Goal carries its Author fallback under CA-D-276-CORE_META_MODEL-DELIVERY--use-economical-yaml-frontmatter **in** `current_scope_unit` **and** the Project Scope Unit **in** `claim_target_scope_unit`; do **not** register the Author as a Scope Unit **or** infer either value from the filename.

## Details
