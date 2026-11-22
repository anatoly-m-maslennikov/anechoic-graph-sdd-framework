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
  status: "archived"
  version: 6
  updated_at: "2026-11-22T10:29:51.118182+00:00"
---

## Summary

Use authoritative inputs for Python import resolution

## Objective

Identify the source for ordered Python search paths and previous-image dependencies. Use that authority to remove duplicated configuration from the Project Manifest. Verify graph edges, unresolved imports, and release compatibility.

## Target

Each child uses one Python root in its own directory. Verify Engine Studio, Release, and Setup independently under AN-S-3310@1.

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
