---
identity:
  atom_id: AN-S-2329
context:
  container:
    component: C46
  tier: 4
  lens: SWD
state:
  status: active
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Keep Workbench frontend files small

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Structure authored HTML, CSS, JavaScript, TypeScript and Svelte by responsibility. Split above 300 lines is strongly recommended and above 500 mandatory; generated build files, lockfiles, vendored sources and frozen history are excluded. Start with a small reusable component palette, separating components, stateful behavior and styles when responsibilities differ, without arbitrary wrappers/fragments for line count. Use Svelte for structured HTML; use a Python HTML builder only when selected frontend tools cannot structure it.
