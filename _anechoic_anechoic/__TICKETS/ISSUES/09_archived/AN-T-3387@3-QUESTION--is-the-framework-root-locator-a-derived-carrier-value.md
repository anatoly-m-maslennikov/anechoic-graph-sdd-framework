---
atom_family: TKT
atom_id: AN-T-3387
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:18:40 +0400
---
## Summary

Is the Framework root locator a derived Carrier value?

# Is the Framework root locator a derived Carrier value?

should D-370's mandatory Framework control-root locator be removed as redundant **or** retained as an explicitly derived, non-authoritative Carrier value?

## Evidence

D-317 fixes the Project-specific Framework root. D-370 nevertheless requires its locator **in** Framework Instance Settings **and** disallows choosing another authority root. D-361 stores explicit instance choices **and** forbids derived structural values as independently editable settings. D-267 requires a fully address-derived Artifact Property **to** have one Carrier encoding. the inspected authority does **not** establish a separate editable root choice **or** the exact exception that would make this locator a checked derived value.

## Principle check

CA-M-002 rejects duplicate authority; CA-M-005 rejects an unnecessary parameter; CA-M-006 requires the locator **and** placement rules **to** agree. a derived readability value is **not** automatically competing authority, but labeling it derived does **not** establish its missing Carrier responsibility **or** authorize an arbitrary new field.

## Disposition

preserve D-370 pending the explicit retained-field **or** retirement decision. do **not** add another root selection, infer a configurable authority root, **or** edit current Settings merely **to** satisfy the old locator rule.
