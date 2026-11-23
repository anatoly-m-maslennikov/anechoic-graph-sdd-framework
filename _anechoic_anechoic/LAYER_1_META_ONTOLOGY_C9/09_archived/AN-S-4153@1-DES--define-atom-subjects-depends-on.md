---
atom_family: SPEC
atom_id: AN-S-4153
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Atom Subjects Depends On

## Claim scope

Direct dependency links under Atom Subjects.

## Claim

Atom Subjects Depends On is the zero-or-more direct dependency reference collection under Subjects. Each link preserves its target identity and does not create a separate Subject object.

### Formal claim

```text
Atom.Subjects.Depends On[string]{0+}
```

## Details

Source meaning: CA-R-1198, CA-R-655. Scope-specific constraints remain in their governing Rs.
