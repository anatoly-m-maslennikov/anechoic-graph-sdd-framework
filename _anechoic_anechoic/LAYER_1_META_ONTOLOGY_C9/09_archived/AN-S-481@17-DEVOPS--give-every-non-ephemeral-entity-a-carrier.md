---
atom_family: SPEC
atom_id: AN-S-481
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 17
  updated_at: 2026-10-30 14:45:35 +0400
---
## Summary

Give every non-ephemeral Entity a Carrier

## Claim scope

non-ephemeral Entities.

## Claim

Every represented non-ephemeral Entity has at least one declared Carrier or a location within a shared Carrier. Reusable D Policies may define that binding for an entire Object kind and its dependent properties; individual D Decisions govern bounded exceptions. The governed Subject names the represented entity, not an extra representation node.

## Details

a binding **may** use a shared Carrier **or** a location within it. A carried Property does not require a separate file or authored CARRIES edge. Its representation follows the applicable owner/property Policy. A derived property can be represented in a Projection without making the Projection authoritative for its source. Occurrents themselves are excluded; retained information about them follows CA-D-654.
