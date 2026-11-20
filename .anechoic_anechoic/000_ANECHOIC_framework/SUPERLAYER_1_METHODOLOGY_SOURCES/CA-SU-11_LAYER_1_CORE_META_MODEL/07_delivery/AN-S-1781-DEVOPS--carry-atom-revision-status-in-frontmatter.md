---
identity:
  atom_id: AN-S-1781
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: active
  version: 26
  updated_at: 2026-11-09 00:51:00 +0400
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
