---
identity:
  atom_id: CA-R-3189
  ref_id: CA-R-3189@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:16.294215+00:00'
destination:
  file:
    name: CA-R-3189@1-draft-CORE_META_MODEL-REQUIREMENT--resolve-package-exports-and-filename-visibility.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Resolve package exports and filename visibility

## Claim

### Prose Claim

When SPEC declares a Package export list, cross-package callers use that list. An explicitly empty list closes cross-package access. A Contract with no export list, such as a latency guarantee, leaves filename-based visibility in effect. Without a SPEC export list, root modules can self-declare visibility as `<name>__<visibility>.<extension>`, with reserved values `internal` and `public`; only marked root modules are eligible for cross-package access in this case. Other Packages use the internal default when neither an export list nor filename marker is present. Use the normal Python module name including its suffix, such as `from billing import orders__public`.

## Details

Acceptance: a nonempty SPEC list permits an otherwise authorized listed entry and excludes an unlisted entry; an empty list denies all cross-package access. A latency-only Contract does not close filename-based access: `orders__public.py` can be imported by its normal suffixed name, subject to caller rules. A root module without a marker is not eligible under the filename fallback.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
