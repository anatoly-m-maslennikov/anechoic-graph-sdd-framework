---
atom_family: SPEC
atom_id: AN-S-1825
container:
  component: C58
tier: 3
context:
  template: action
  lens: DOM/MTD
state:
  status: active
  version: 22
  updated_at: 2026-10-27 19:59:45 +0400
---
# Summary

Assess Atom update identity

## Operation

This read-only Action reports whether a proposed Summary or Content Role differs from the selected Atom. A changed Draft Summary or Content Role results in a new identity promoted at Version 1; an existing Draft with unchanged Summary and Content Role retains its Version. This observation is not a semantic change-class assessment or a prerequisite for Update, direct editing, or promotion. The Action does not persist changes or select a Workflow continuation.
