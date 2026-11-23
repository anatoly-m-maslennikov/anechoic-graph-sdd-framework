---
atom_family: SPEC
atom_id: AN-S-4440
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: '2026-11-12T03:12:38.793008+00:00'
---
## Summary

Declare Code Synopsis Form

## Claim

### Prose Claim

A Code Synopsis identifies one or more unambiguous code locations in its Project context. Its Claim describes the referenced code at the identified context and state. The referenced code determines actual behavior and structure. A Python Formal Claim is admitted when its consumers support Python. CFEL remains admitted during migration.

### Formal Claim

```CFEL
# model
Atom.Header.Context.Form :: Code Synopsis;

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Header.State.Status :: Resolved;

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Summary ;> Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim;

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim{::1}:: []{::0};
Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.*[string, in (Formal Claim, Prose Claim)]{::1..2};

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Prose Claim{::0..1}:: {::1};
Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Prose Claim.*[]{::0};

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Formal Claim{::0..1}:: {::1};
Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Formal Claim.*[]{::0};

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Prose Claim ;> Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Formal Claim;

IF (Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Formal Claim {=1}) THEN (
FENCED_LABELS(Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Code Synopsis)).Content.Claim.Formal Claim):: [in (CFEL, python)]{::1}
);

# instances
FOR EACH $a[<Atom>, (.Header.Context.Form = Code Synopsis)]:
(
    $a.Header.Context.Role:: [in ("Analysis and Advisory")]{::1}
)
```

## Semantics

A Code Synopsis is an authored, concise explanation of an actual code area and its relevant rationale.

For a Code Synopsis, **Resolved** means the review is complete:

- Every finding that needs fixing or adopting is covered by Active C or RMEDO Atoms; or
- The review found nothing to fix or adopt.

Drafts do not count as handoff. The resulting Atoms keep their own statuses. Resolved closes the Code Synopsis review; it does not mean the resulting Concerns are resolved or the RMEDO changes are implemented.
