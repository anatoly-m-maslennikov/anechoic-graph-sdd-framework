---
atom_family: SPEC
atom_id: AN-S-3432
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Validate declared Scope Unit tree before cutover

# Summary

Validate declared Scope Unit tree before cutover

## Scope

Validation of the one proposed authoritative TOML tree delta selected by CA-O-139 and prepared by CA-O-140.

## Claim

The Tool **must** reject a proposal unless its resulting declarations form a valid acyclic parent tree and preserve the declared ordering and path constraints.

## Details

- Scope Unit identity is `scope_unit_name`; it is unique. Every non-root parent must resolve to a declared Scope Unit in the resulting tree; a unit cannot parent itself or any ancestor.
- `scope_unit_type` is exactly `Ordered` or `Unordered`. `local_order` is required and unique among siblings only for `Ordered` units, and is forbidden for `Unordered` units. `navigational_order_number` is presentation data and does not establish type or parent order.
- The resulting `authority_path` and `delivery_path` are explicit, nonempty, and reported separately. Existing folders, missing folders, and unlisted implementation paths are observations requiring disposition, never implicit declaration authority.
- The assessment enumerates affected Scope Unit identities, incoming Atom/Goal/reference links, declared authority paths, delivery/implementation paths, and observed Carrier paths. It reports unresolved or broken members rather than silently dropping them.
