---
atom_family: SPEC
atom_id: AN-S-2137
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 23
  updated_at: 2026-11-11 15:27:11 +0400
---
## Summary

Place Carriers by Applicable Status Delivery

## Claim

### Prose Claim


Carrier placement where an applicable qualified Artifact Status model exists or does not exist.


**when** an Atom has Draft or Archived Status, place its Markdown Carrier in the owning Scope Unit’s shared Content Role `draft` or `archived` directory respectively, regardless of its logical container. For a Current Atom, place its Carrier locally in its actual container according to its applicable Status mapping; CA-D-461 retains its stated boundary for root Plan terminal Statuses. **when** an applicable qualified Artifact Status model exists for another Artifact, its Carrier placement **must** follow the most specific applicable Delivery rule for that Artifact Type; **only when** no more-specific mapping exists, Active uses the canonical current directory **and** another Status uses its lowercase Status subdirectory. **when** no applicable qualified Status model exists, Carrier placement **must not** derive a Status directory from absent Status. These placement rules do not authorize independent legacy moves or rewrites.
