---
identity:
  atom_id: AN-T-2931
context:
  container:
    atom: AN-T-2923
  template: task
state:
  status: backlog
  version: 1
  updated_at: '2026-11-20T16:57:42.524056+00:00'
---
## Summary

Recover and migrate authored native Atom data

## Work

After AN-T-2930, match native Carriers to exact earlier revisions in Git.
Recover admitted authored fields. Record source commit, path, exact
reference, and disposition for gaps and held values.

Rehearse and apply the Carrier migration. Verify identities, revision
references, Content, Relations, Package bindings, and derived paths.
Keep unresolved Drafts in legacy and preserve archived history.
