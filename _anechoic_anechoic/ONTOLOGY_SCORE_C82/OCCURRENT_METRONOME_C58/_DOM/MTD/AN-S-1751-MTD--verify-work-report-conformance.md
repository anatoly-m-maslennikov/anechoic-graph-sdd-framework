---
atom_family: SPEC
atom_id: AN-S-1751
container:
  component: C58
tier: 4
context:
  lens: DOM/MTD
state:
  status: active
  version: 3
  updated_at: '2026-11-25T20:32:21.769241+00:00'
---

## Summary

Verify Work Report conformance

## Claim

### Prose Claim

For a native Work Report, check the `work_report` Ticket Asset Template, its own Summary, and the Container and placement rules in AN-S-3160. Check that the report records actual changes, checks performed, results, and remaining gaps. Require evidence for the reported checks and results. Check Task Status independently.

For legacy Plan / Work Report carriers, apply these checks:

- Resolve exactly one IS_WORK_REPORT_FOR target: the base Atom ID of an admitted Plan with Form Plan.
- Check the report’s distinct ID, matching Summary and matching Container.
- Check actual changes, performed checks, results and remaining gaps in Details. Subheadings remain Markdown text.
- Accept updates during execution and completion with explicit remaining gaps.
- Check report Status against reporting completion or abandonment. Check the Task’s Status independently.
- Reject version-qualified Task references, unresolved targets, intended-work instructions presented as actual results, or invented checks.
- Accept different Tasks with the same Summary and Container when the explicit Relation identifies the correct Task.

Record the checked identities, results and supporting evidence.
