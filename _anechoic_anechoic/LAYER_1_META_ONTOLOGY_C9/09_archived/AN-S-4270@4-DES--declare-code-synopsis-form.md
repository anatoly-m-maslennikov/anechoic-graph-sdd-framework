---
atom_family: SPEC
atom_id: AN-S-4270
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 14:38:45 +0400
---

## Summary

Declare Code Synopsis Form

## Claim

### Prose Claim

A Code Synopsis identifies one or more unambiguous code locations in its Project context. Its Claim describes the referenced code at the identified context and state. The referenced code determines actual behavior and structure.

### Formal Claim

```CFEL
# model
Atom/(.Header.Form := Code Synopsis);

Atom/(.Header.Form := Code Synopsis).Header.Status: Resolved;

Atom/(.Header.Form := Code Synopsis).Content.Summary ;> Atom/(.Header.Form := Code Synopsis).Content.Claim;

Atom/(.Header.Form := Code Synopsis).Content.Claim{::1}:: []{::0};
Atom/(.Header.Form := Code Synopsis).Content.Claim.*[string, in (Formal Claim, Prose Claim)]{::1..2};

Atom/(.Header.Form := Code Synopsis).Content.Claim.Prose Claim{::0..1}:: {::1};
Atom/(.Header.Form := Code Synopsis).Content.Claim.Prose Claim.*[]{::0};

Atom/(.Header.Form := Code Synopsis).Content.Claim.Formal Claim{::0..1}:: {::1};
Atom/(.Header.Form := Code Synopsis).Content.Claim.Formal Claim.*[]{::0};

Atom/(.Header.Form := Code Synopsis).Content.Claim.Prose Claim ;> Atom/(.Header.Form := Code Synopsis).Content.Claim.Formal Claim;

IF (Atom/(.Header.Form := Code Synopsis).Content.Claim.Formal Claim {=1}) THEN (
FENCED_LABELS(Atom/(.Header.Form := Code Synopsis).Content.Claim.Formal Claim):: [in (CFEL)]{::1}
);

# instances
Atom/(.Header.Form := Code Synopsis)//$synopsis.Header.Role:: [in ("Analysis & Advisory")]{::1}
```

## Semantics

A Code Synopsis is an authored, concise explanation of an actual code area and its relevant rationale.

For a Code Synopsis, **Resolved** means the review is complete:

- Every finding that needs fixing or adopting is covered by Active C or RMEDO Atoms; or
- The review found nothing to fix or adopt.

Drafts do not count as handoff. The resulting Atoms keep their own statuses. Resolved closes the Code Synopsis review; it does not mean the resulting Concerns are resolved or the RMEDO changes are implemented.
