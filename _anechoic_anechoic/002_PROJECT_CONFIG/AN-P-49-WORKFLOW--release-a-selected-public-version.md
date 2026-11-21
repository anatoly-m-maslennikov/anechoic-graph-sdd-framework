---
atom_family: PMETA
atom_id: AN-P-49
structure:
  container:
    component: C27
context:
  template: workflow
state:
  status: active
  version: 22
  updated_at: '2026-11-21T21:49:04.407565+00:00'
---

# Summary

Prepare public release drafts

## Operation

Public Release prepares a detailed Pull Request description and a brief Version History entry for the selected Git comparison.

Resolve the base and head to immutable commits and read the selected Version from the pinned head. Read completed Task and Epic content directly from Git. Delegate a Luna review of the pinned diff against those tickets to identify missed changes. Render both drafts from reviewed content bound to the same commits.

The result is draft text for the Operator. This Workflow does not change repository files, commit, push, create or update a Pull Request, run a public suite, or use Journal. A failed or mismatched comparison stops without a draft.
