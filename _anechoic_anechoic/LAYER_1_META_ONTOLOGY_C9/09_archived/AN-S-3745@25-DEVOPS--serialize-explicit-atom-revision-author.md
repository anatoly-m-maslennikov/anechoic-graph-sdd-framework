---
atom_family: SPEC
atom_id: AN-S-3745
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 25
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Serialize Explicit Atom Revision Author

# Summary

Serialize Explicit Atom Revision Author

## Scope

Markdown Atom Carriers.

## Claim

a Markdown Atom Carrier **must** serialize **`=1`** resolved Author as the top-level frontmatter Property `author`; apply the applicable Author default during authoring rather than leaving the accepted Revision dependent on an omitted Author.

- encode `author` as **=1** nonempty YAML string equal **to** a name **in** the Project's Operator registry under CA-D-494, **not** a list **or** a null value.
- validate Author by exact registry membership. an unlisted name fails membership; unavailable **or** invalid registry context leaves the check incomplete. do **not** require an additional Actor identity lookup **or** copy the registered role into Atom frontmatter.

## Details
