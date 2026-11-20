---
identity:
  atom_id: AN-T-1959
context:
  container:
    component: C15
  tier: 4
  template: question
state:
  status: resolved
  version: 3
  updated_at: 2026-11-10 22:25:42 +0400
---

## Summary

Which declared objects replace old Tool permission targets?

## Concern

The TOOLS, TOOL_WORKFLOWS and PROJECT_TOOLS delegation Drafts still name retired or unverified model objects in their exact target whitelists. Examples include Graph Rule, Tool, Scope Unit.Path and obsolete Atom property paths. An unresolved address grants no permission; substituting a broad parent would change the allowed work.

## Details

Keep these three permission Drafts unadopted and their Current declarations unchanged. Their old Tool implementations and local specifications are already deferred. Resolve their exact targets when those Tools are rebuilt, using established Model declarations rather than aliases or invented entities. Other Engine source work continues.

Blast radius: the permission refresh in R2655, R2657 and R2658 only. No Scope Unit moves, Current source changes or runtime changes.

## Resolution

The Operator clarified that the old Tools are fully retired, not deferred for rebuilding. Withdraw the R2655, R2657 and R2658 permission-update Drafts and preserve their exact bytes in history. No permission-target migration or old-Tool implementation is queued.

This answers the pending permission question. The Operator confirmed that full retirement is already complete. No additional old-Tool retirement, permission migration or rebuilding work is queued by this Question.
