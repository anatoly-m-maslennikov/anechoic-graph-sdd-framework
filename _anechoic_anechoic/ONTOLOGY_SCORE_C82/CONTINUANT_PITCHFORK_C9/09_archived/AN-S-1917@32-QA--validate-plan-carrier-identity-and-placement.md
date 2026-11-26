---
atom_family: SPEC
atom_id: AN-S-1917
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 32
  updated_at: "2026-11-25T21:19:16.322164+00:00"
---
## Summary
Validate Plan Carrier identity **and** placement

## Claim

Check planning Ticket identity, placement, and containment under AN-S-3160 and AN-S-1604.

- Read the ID, Status, Version, and Container from the Ticket. A companion folder shares the Carrier basename and holds the descendants. Moving a Carrier preserves the declared containment and historical revisions.
- Check each filename and destination, including the derived Draft or Archive marker and Summary slug. Report a mismatch and keep the Ticket indexed under its declared Container.
- When a planning Ticket becomes Done or Canceled, check that Current nonterminal descendants become Canceled and terminal descendants keep their states. Check that referenced Tickets outside the tree retain their states.
- Check that changing Label or placement preserves the Ticket ID and its intended work. Verify the Definition of Done against its own evidence under AN-S-2306.
