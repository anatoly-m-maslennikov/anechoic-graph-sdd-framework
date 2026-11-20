---
identity:
  atom_id: AN-T-2925
context:
  container:
    atom: AN-T-2923
  template: task
state:
  status: "active"
  version: 1
  updated_at: "2026-11-20T14:13:47.272088+00:00"
---
## Summary

Compile separate entity and Property declarations

## Work

After AN-T-2924, update Manifest Compiler and Model Host. Have the
compiler enforce the whitelist, assemble inherited Properties into the
public Model types, and generate the validators and derived Ref ID.
Verify that Model Host loads the resulting generation.

## References

AN-S-3089, Manifest Compiler. AN-S-3090, Model Host.
