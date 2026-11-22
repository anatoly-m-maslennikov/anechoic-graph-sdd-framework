---
atom_family: TKT
atom_id: AN-T-2982
container:
  component: C59
priority: 2
context:
  template: code_spec_mismatch
state:
  status: backlog
  version: 1
  updated_at: '2026-11-22T10:13:27.725125+00:00'
---
## Summary

Populate the Kernel live Lifecycle Run view

## Claim

### Prose Claim

AN-S-2551@10 and AN-S-2243@1 require SQL access to live Lifecycle Run
list fields for the selected Project. Kernel Mixer creates `live_runs`
and defines `set_live_runs`. The method has no production caller in
the current Realization.

## Work

Identify the admitted Lifecycle Run source and publish the Project's
Run ID, session, Tool and status to Kernel. Verify that a real query
can see an active Run from its own Project and that the rows follow
the current retention rules. Preserve the admitted list fields.

Verify AN-S-2551@10 before replacing the archived AN-S-2551@8
reference in the Kernel Spec Binding. See AN-T-2944 and AN-T-2948.
