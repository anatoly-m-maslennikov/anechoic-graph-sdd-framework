---
atom_family: SPEC
atom_id: AN-S-1728
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: active
  version: 34
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Validate Atom-set Selection **and** the spec Alias

## Claim

### Prose Claim

the four ownership **and** targeting selections for a Scope Unit, including the `spec` alias.


**Claim checked.**

ownership **and** Claim targeting produce their respective direct **and** recursive Atom sets, **and** the alias `spec` selects **only** Active RMED Subtree-targeting Atoms.

## Details

### Test case

construct Scope Unit `A`, its child Scope Unit `A_CHILD`, a sibling Scope Unit `B`, **and** nested Atom Collections inside `A`. the fixture Scope Units are Unordered. use the following distinct source Atoms; resolve each target Scope Unit from the Atom’s one active Subject under CA-R-2102; derive its current Scope Unit from containment. `d`, `e`, **and** `f` have Role Requirement **and** Form Demand under CA-R-932@37, with applicable Demand conditions satisfied. The remaining rows are valid Current-scope Atoms with admitted non-relational Forms; a target equal to the current Scope Unit does **not** make them Relational.

| Atom | Current Scope Unit | Placement | Claim Target Scope Unit | Role | Status |
|---|---|---|---|---|---|
| `a` | `A` | directly under `A` | `A` | Requirement | Active |
| `b` | `A` | nested Atom Collection | `A` | Method | Active |
| `c` | `A_CHILD` | directly under `A_CHILD` | `A_CHILD` | Evaluation | Active |
| `d` | `B` | directly under `B` | `A` | Requirement | Active |
| `e` | `B` | directly under `B` | `A_CHILD` | Requirement | Active |
| `f` | `A` | directly under `A` | `B` | Requirement | Active |
| `g` | `A` | Draft placement | `A` | Requirement | Draft |
| `h` | `A` | directly under `A` | `A` | Plan | Active |
| `i` | `A` | Archived placement | `A` | Delivery | Archived |

derive **all** four sets for `A` **and** the alias `spec`. repeat **after** moving `a` into a nested Atom Collection under `A` **and** changing **only** numeric Tiers; repeat with narrower **and** explicitly grouped composite applicability restrictions **in** Claim.Prose Claim while retaining the active Subjects; repeat with `b` assigned **every** RMED Role while retaining its other properties. **then** omit `B` from the claimed-complete source frontier, treat a Hub Plan as a Scope Unit, replace targeting with ownership, copy a selected Atom as new authority, omit an active Subject, infer a different target from Claim text, use an unresolved structural target **or** cyclic ancestry, **or** register `spec` as a separate Entity.

### Acceptance criteria

the results **must** be:

| Selection | Members |
|---|---|
| Owned Atoms | `a, b, f, g, h, i` |
| Targeting Atoms | `a, b, d, g, h, i` |
| Subtree-owned Atoms | `a, b, c, f, g, h, i` |
| Subtree-targeting Atoms | `a, b, c, d, e, g, h, i` |
| `spec` alias | `a, b, c, d, e` |

collection nesting, textual applicability restrictions, **and** numeric-Tier-only changes **must not** alter those results. `spec` **must not** create a separate Entity, independently maintained Atom set, **or** source of authority. incoming `d` **and** `e` retain ownership under `B`; outgoing `f` remains owned by `A` **without** entering its Targeting Atoms **or** `spec`. incomplete source coverage, missing, multiple **or** unresolved active Subjects, targets inferred from Claim text, cyclic ancestry, ownership/target substitution, **and** duplicate authority fail explicitly.

### Failure disposition

report the source Revision, selected Scope Unit, expected set, **and** exact missing, extra, duplicated, **or** unresolved member; do **not** silently return a complete result **or** rewrite source ownership.
