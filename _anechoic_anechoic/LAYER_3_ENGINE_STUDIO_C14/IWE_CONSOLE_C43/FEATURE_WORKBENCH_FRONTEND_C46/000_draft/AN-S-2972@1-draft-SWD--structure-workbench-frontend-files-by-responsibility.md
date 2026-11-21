---
atom_family: SPEC
atom_id: AN-S-2972
structure:
  container:
    component: C46
  tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 1
  updated_at: '2026-11-13T20:51:01.763167+00:00'
---
## Summary

Structure Workbench frontend files by responsibility

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Structure authored HTML, CSS, JavaScript, TypeScript and Svelte by responsibility. Splitting files above 300 lines is strongly recommended. Split files above 500 lines. These limits exclude generated build files, lockfiles, vendored sources and frozen history.

Start with a small reusable component palette. Separate components, stateful behavior and styles when their responsibilities differ. Do not add arbitrary wrappers or fragments to meet a line count.

Use Svelte to structure HTML. Use a Python HTML builder only when the selected frontend tools cannot structure it.
