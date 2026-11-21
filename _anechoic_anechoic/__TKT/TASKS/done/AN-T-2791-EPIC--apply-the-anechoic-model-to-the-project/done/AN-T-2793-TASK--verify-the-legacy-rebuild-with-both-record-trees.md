---
atom_family: TKT
atom_id: AN-T-2793
structure:
  container:
    atom: AN-T-2791
  priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-20T02:56:40.782516+00:00'
---
## Summary

Verify the legacy rebuild with both record trees

## Work

Compare the protected inputs and run the clean Local Release rebuild on an isolated coexistence checkout.

Verify the protected input paths and digests with the original Settings
through the clean rebuild. For the final startup check, CA-C-758 permits
one free port in the isolated copy. Record the port exception and verify the
original Settings bytes after the check. Keep the live service running.

## References

CA-P-3075, CA-C-758.
