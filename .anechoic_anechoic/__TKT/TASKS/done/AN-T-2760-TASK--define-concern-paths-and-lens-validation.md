---
identity:
  atom_id: AN-T-2760
context:
  container:
    atom: AN-T-2757
  tier: 3
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-18T21:56:29.201112+00:00'
---
## Summary

Define Concern paths and lens validation

## Work

Verify
   the three Concern fields, full paths, and both hops in
   `Model/Graph/Node//Artifact`. Cover absent, inherited, and explicit
   empty lens whitelists. Accept SPEC with DES and SWE. Accept SWE with
   SWD and QA when DevOps is omitted. Reject sibling DES and SYS because
   both cover DOM.

## References

CA-P-3074.
