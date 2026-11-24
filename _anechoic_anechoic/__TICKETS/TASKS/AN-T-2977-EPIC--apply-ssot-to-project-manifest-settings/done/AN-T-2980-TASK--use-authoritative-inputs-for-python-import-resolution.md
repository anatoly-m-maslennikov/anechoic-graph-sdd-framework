---
atom_family: TKT
atom_id: AN-T-2980
container:
  atom: AN-T-2977
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 9
  updated_at: "2026-11-22T11:06:18.590565+00:00"
---

## Summary

Use authoritative inputs for Python import resolution

## Objective

Identify the source for ordered Python search paths and previous-image dependencies. Use that authority to remove duplicated configuration from the Project Manifest. Verify graph edges, unresolved imports, and release compatibility.

## Target

Each child uses one Python root in its own directory. Verify Engine Studio, Release, and Setup independently under AN-S-3310@4.

## Single-root comparison

On 880 parsed Python files, the current roots resolve 2,528 internal
import occurrences and leave 175 unresolved. With only the Project
root, 1,627 previously resolved occurrences lose their target across
579 files. The scan held the previous-image declarations constant.

The earlier comparison measured one root over the whole
repository. Retain the current roots until the three-child migration passes.

## Cutover checks

- Use one module identity for each first-party module. Migrate imports,
  dynamic targets, and test patch targets together.
- Verify checkout and packaged entry points with only the owning child's
  Python root on the configured Python search path. Preserve selected
  previous-image compatibility.
- Compare Import Graph resolution in the three child contexts before cutover.
  Classify remaining unresolved imports and compare internal targets.

## First migration pass

Runtime Setup and Local Release use package imports. Public Release tests
use the normal Package identity. C61 callers and test patch targets use the
same qualified Import Graph module names. Focused Setup, Release, and C61
checks passed. The root-only Journal test still hits a Model Engine alias.

On the current checkout, the single-root comparison loses 1,537 internal
resolutions across 545 Python files. The current Manifest roots remain in
use. The next pass migrates shared Model and Project binding imports with
their consumers, then verifies the MCP and compiler launch paths against the
selected framework root and the previous-image contract.

## Static QA after migration

- Use the child root definitions and existing Import Graph resolution to
  check cross-child Python imports. Report the importing file, line and
  target. Check sibling targets even when a child-only search cannot
  resolve them.
- Add the check to the existing static QA phase. Verify that a same-child
  import passes and a cross-child import fails. Evaluate Import Linter's
  independence contract if it simplifies the check while preserving
  the same root definitions.
- Exercise each uv launcher from outside its child directory. Verify its
  effective Python root and environment. Cover dynamic and previous-image
  entry points with targeted launch tests.

## Verification

AN-S-3037@17 removes the ordered Python root list. The graph resolves each child against its own root and lock. Historical imports stay scoped to the predecessor selector. Static QA rejects sibling Python imports. The immutable predecessor claim selection and 15 graph checks passed.
