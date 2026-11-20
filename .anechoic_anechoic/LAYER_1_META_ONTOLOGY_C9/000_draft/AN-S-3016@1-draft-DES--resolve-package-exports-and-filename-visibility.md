---
identity:
  atom_id: AN-S-3016
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:16.294215+00:00'
---
## Summary

Resolve package exports and filename visibility

## Claim

### Prose Claim

When SPEC declares a Package export list, cross-package callers use that list.
An explicitly empty list closes cross-package access. A Contract with no export
list, such as a latency guarantee, leaves filename-based visibility in effect.

Without a SPEC export list, a Package uses the Internal default until it has a
marked root Module. The filename has the form
`<name>__<visibility>.<extension>`, with visibility `internal` or `public`.
Once the Package has a marked root Module, only its marked root Modules are
eligible for cross-package access. Use the normal Python module name including
its suffix, such as `from billing import orders__public`.

## Details

- A nonempty SPEC list permits an otherwise authorized listed entry and excludes
  unlisted entries. An empty list denies all cross-package access.
- A Package with neither a SPEC list nor a marked root Module uses Internal
  access for its unmarked Modules.
- Adding `orders__public.py` at the Package root makes it eligible by its
  suffixed name and closes cross-package access to unmarked Modules.
  Caller rules still apply.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
