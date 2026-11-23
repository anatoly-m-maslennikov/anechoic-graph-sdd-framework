---
atom_family: SPEC
atom_id: AN-S-2329
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Keep Workbench frontend files small

## Claim scope

The Workbench frontend.

## Claim

### Prose Claim

Structure Workbench HTML, CSS, JavaScript, TypeScript and Svelte by responsibility. Splitting a source file above 300 lines is strongly recommended; above 500 lines it is mandatory. Generated build files and dependency lockfiles are not authored source.

Create a small reusable component palette from the start and use it in the page. Split UI components, stateful application behavior and styles where their responsibilities differ; do not create wrappers or arbitrary fragments just to satisfy a line count.

Svelte components provide structured HTML for this frontend. A Python HTML builder is only needed if HTML cannot be structured with the selected frontend tools.
