---
atom_family: TKT
atom_id: AN-T-2002
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: archived
  version: 3
  updated_at: 2026-10-20 21:48:23 +0400
---
## Summary

Which evidence binds Draft origin to its own history

# Summary

Which evidence binds Draft origin to its own history

## Concern

Mutable Draft provenance can describe an admitted origin but cannot prove that an arbitrary valid archive belongs to that Draft. Options considered: trust the mutable map; add a self-hash/signature without a trust authority; or bind admitted Draft outputs to immutable retained Atom history. The earlier review chose the third, at 88% design confidence, because it used existing history rather than a second identity registry and closed the then-identified counterexamples. This remains historical discussion, not current authority. Each current Draft carries a pre-addressable history-entry reference; that entry binds its exact output locator and digest, direct parent lineage and origin. Lifecycle effects are the admitted writers of retained history. Out-of-band Draft bytes without a matching entry fail closed; an Operator able to reauthor both authority and history is outside the untrusted-request boundary. P1675/P1676 defined and reviewed the minimum source contract before code. A self-hash alone is not claimed to authenticate origin.

### Publication choice

The next narrow review found that a pre-write consuming entry could claim nonexistent output. The earlier publication review chose a non-consuming private pending transition over a multi-file atomic-publication claim: reserve the exact planned output and request, observe the actual output, then append finalized retained history. Pending repair binds the same identity on retry; it is ephemeral runtime context, not a new identity registry or another Journal. Only finalized history consumes the Draft head. P1681 bound this necessary repair before P1676 accepted source and P1677 implemented it. This discussion is retained as historical evidence.

## Resolution

This Question is superseded by the later human decision recorded through CA-D-568 and CA-D-570: retained Draft history or lineage is not a promotion gate. The later same-identity marker decision likewise supersedes the retained-history choice: `CA-R-123@4-draft` promotes to canonical `CA-R-123` Version 4 with the exact current predecessor archived, subject to the explicit target, Version and digest bindings. This resolution records supersession only; it introduces no separate runtime claim.

## Evidences

P1638's saved rejected review and independent origin adjudication identify the exact branches and source claims. Prior partial passing evidence is retained, not converted into a clean pass.

## Blast radius

The bounded Draft identity promotion path and its source history contract. No mandatory image/permission gate is bypassed and no broad identity registry or new Journal is introduced.
