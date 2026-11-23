---
atom_family: SPEC
atom_id: AN-S-1781
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Carry Atom Revision Status in frontmatter

# Summary

Carry Atom Revision Status in frontmatter

## Scope

the Status property carried by an Atom Revision.

## Claim

**every** Atom Revision **must** carry **`=1`** explicit `status` value **in** its own Markdown frontmatter.

- the value **must** belong **to** the applicable Content Role **and** Type Status model.
- placement **must** agree under CA-D-466 **and** its specific Delivery rules; it is **not** a second Status source.
- another Revision **or** a containing Hub **must not** override this Revision's carried Status.

- encode `status` as **=1** nonempty YAML string using the exact value admitted by the selected Status model. do **not** accept a list, null, **or** another Revision's value as this Revision's Status.

## Details
