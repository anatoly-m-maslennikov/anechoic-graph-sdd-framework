---
atom_family: SPEC
atom_id: AN-S-1744
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 31
  updated_at: "2026-11-25T22:00:01.307529+00:00"
---
## Summary

Effective-priority selection

## Claim

Check Ticket Priority under AN-S-3169 and conflict selection under AN-S-1646.

- Accept an integer Ticket Priority and reject a string or Boolean in its place. Check the serialized value and the selected criteria separately.
- Compare two otherwise equal Tickets from different Component levels. Verify that ancestry adds no implicit priority.
- Check the default Operator decision path, a uniquely eligible automatic result, ties, incomparable candidates, missing evidence, and incompatible external obligations. Report the actual result without changing an Atom during evaluation.
