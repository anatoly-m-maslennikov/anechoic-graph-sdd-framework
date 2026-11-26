---
atom_family: SPEC
atom_id: AN-S-1781
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 26
  updated_at: "2026-11-25T22:07:23.522445+00:00"
---
## Summary

Carry Atom Revision Status in frontmatter

## Claim

### Prose Claim


the Status property carried by an Atom Revision.


Every Atom Revision carries exactly one explicit Status value at its declared Header path in its own Markdown frontmatter.

- the value **must** belong **to** the applicable Content Role **and** Type Status model.
- placement **must** agree under CA-D-466 **and** its specific Delivery rules; it is **not** a second Status source.
- another Revision **or** a containing Hub **must not** override this Revision's carried Status.

- Encode Status as one nonempty YAML string using the common named-value encoding. Its decoded value resolves to exactly one Status admitted by the applicable model. A list, null or another Revision’s value is invalid.
