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
  version: 3
  updated_at: "2026-11-22T10:14:47.453390+00:00"
---

## Summary

Use authoritative inputs for Python import resolution

## Objective

Identify the source for ordered Python search paths and previous-image dependencies. Use that authority to remove duplicated configuration from the Project Manifest. Verify graph edges, unresolved imports, and release compatibility.

## Target

Use one Python root. Check the Project root (`.`) as the default. Measure old-root dependencies and preserve previous-image import handling.

## Single-root comparison

On 880 parsed Python files, the current roots resolve 2,528 internal
import occurrences and leave 175 unresolved. With only the Project
root, 1,627 previously resolved occurrences lose their target across
579 files. The scan held the previous-image declarations constant.

The target is one Python root. The checkout retains the ordered roots
pending the Operator's cutover decision.
