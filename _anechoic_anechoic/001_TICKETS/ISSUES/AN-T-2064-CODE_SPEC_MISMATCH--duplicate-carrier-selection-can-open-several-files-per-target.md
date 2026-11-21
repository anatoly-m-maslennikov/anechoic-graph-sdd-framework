---
atom_family: TKT
atom_id: AN-T-2064
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-12T12:58:55.273920+00:00'
---
## Summary

Duplicate carrier selection can open several files per target

## Claim

### Prose Claim

CA-M-1006@7 allows one exact file read per selected target. `FEATURE_TOOLS/ATOM_LIFECYCLE/source.py` opens candidate files until `_unique_candidate` finds a valid version, identity and status. A stale or malformed duplicate can cause a second physical read for the same target. `publish.py` also stops indexed Archive replacement lookup on an invalid first match, even if a later result may be valid.
