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

When SPEC declares a Package export list, cross-package callers use that list. An explicitly empty list closes cross-package access. A Contract with no export list, such as a latency guarantee, leaves filename-based visibility in effect. Without a SPEC export list, root modules can self-declare visibility as `<name>__<visibility>.<extension>`, with reserved values `internal` and `public`; only marked root modules are eligible for cross-package access in this case. Other Packages use the internal default when neither an export list nor filename marker is present. Use the normal Python module name including its suffix, such as `from billing import orders__public`.

## Details

Acceptance: a nonempty SPEC list permits an otherwise authorized listed entry and excludes an unlisted entry; an empty list denies all cross-package access. A latency-only Contract does not close filename-based access: `orders__public.py` can be imported by its normal suffixed name, subject to caller rules. A root module without a marker is not eligible under the filename fallback.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
