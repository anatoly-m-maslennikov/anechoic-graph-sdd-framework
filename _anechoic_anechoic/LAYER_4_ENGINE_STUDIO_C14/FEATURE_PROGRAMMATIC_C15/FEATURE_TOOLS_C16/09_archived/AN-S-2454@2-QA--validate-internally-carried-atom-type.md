---
atom_family: SPEC
atom_id: AN-S-2454
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Validate internally carried Atom Type

# Summary

Validate internally carried Atom Type

## Claim

the Carrier validation Tool **must** accept a valid Atom Type carried inside its Markdown file under the applicable Delivery schema **and** reject missing required **or** contradictory representations.

- parse the carried Type without using a filename Type token as its source; a matching token is a valid representation, **not** prohibited duplication.
- remove the required internal value while leaving a valid filename token: reject the Atom.
- alter the token so that it disagrees with the carried Type: reject the mismatch **without** silently selecting the address value.
- a CLI failure reports the affected Property **and** Carrier with a non-zero exit; the Tool **must not** repair the source as part of validation.
