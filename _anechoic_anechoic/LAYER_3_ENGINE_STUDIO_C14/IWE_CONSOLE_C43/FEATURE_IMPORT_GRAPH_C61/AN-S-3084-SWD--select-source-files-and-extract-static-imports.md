---
atom_family: SPEC
atom_id: AN-S-3084
container:
  component: C61
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 3
  updated_at: '2026-11-20T22:44:56.273982+00:00'
---

## Summary

Select source files and extract static imports

## Claim

### Prose Claim

Scan the selected Project's live working tree recursively from its root. Skip dot folders. Recognize executable files by source type, shebang, or executable mode. Recognized source counts even without executable permission. Include all recognized languages independently of parser support. Keep traversal within the Project root. Exclude dependencies, generated and archived copies, caches, and runtime output even when Git tracks them. Apply Git ignore rules to untracked files in a Git Project. The Import Graph configuration can include named authored files that those rules omit. The source boundary and excluded directories still apply.

The first delivery uses Python's standard-library AST parser, which is available in the native Workbench runtime. Inventory JavaScript, TypeScript, and Svelte files, including `.js`, `.mjs`, `.ts`, and `.svelte`, from the first scan. Mark these files unsupported in the first delivery. A later parser must support static imports in JavaScript, TypeScript, and Svelte script blocks. Mark a recognized file without a parser as unsupported. Retain files with zero imports, parse errors, or read errors and distinguish these cases. For a read or parse failure, report the file path and error to stderr.

Read source without executing it. Extract Python `import` and `from … import` statements, including relative imports. For JavaScript and TypeScript, extract static import declarations, including side-effect imports. Include imports in conditional blocks where permitted. Exclude comments, exports, re-exports, dynamic loads, and other execution relationships. An occurrence records source syntax. Mark it type-only only when the whole import is type-only. Keep a mixed value-and-type declaration as a single value occurrence.

## References

[Tier 1 Decision AN-S-3083](../__DES/AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md), [Spec Proposal CA-A-1467](../../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md).
