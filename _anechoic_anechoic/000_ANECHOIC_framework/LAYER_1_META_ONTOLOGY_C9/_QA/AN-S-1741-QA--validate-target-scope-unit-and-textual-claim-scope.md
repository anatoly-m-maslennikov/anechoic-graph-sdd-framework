---
atom_family: SPEC
atom_id: AN-S-1741
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Validate Target Scope Unit **and** textual Claim Scope

## Claim

### Prose Claim

the distinction between an Atom's Claim Target Scope Unit **and** its textual applicability.


**Claim checked.**

**every** Atom has exactly one active Subject; resolve its Claim Target Scope Unit from that Subject under CA-R-2102. Textual applicability belongs in Claim.Prose Claim under CA-D-495 and does not create another structural target.

## Details

### Test case

create an Atom whose active Subject resolves to its current Scope Unit and whose Prose Claim restricts applicability to Python files; repeat with a composite restriction and with an admitted different target. Include a Plan nested in Container Atoms. Then omit or duplicate the active Subject, use an unresolved Subject, or infer a target from the textual restriction alone.

### Acceptance criteria

valid fixtures resolve the target from exactly one active Subject; containment supplies current Scope Unit context. Applicability restrictions and Container Atom nesting do not independently change that target. Invalid fixtures identify the missing, multiple, unresolved, or improperly inferred Subject or target.

### Failure disposition

report the affected Atom **and** target **or** textual-applicability distinction; preserve the source **until** an authorized correction is selected.
