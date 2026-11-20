---
identity:
  atom_id: AN-P-46
context:
  container:
    component: C27
  tier: 3
  template: action
state:
  status: active
  version: 14
  updated_at: 2026-11-09 15:54:30 +0400
---

# Summary

Finalize the actual public history link

## Action

Finalize the actual public history link **means** the mechanical action that either records a no-op for an already present actual PR link or appends a newly created PR’s exact URL to the concise Version History, follows up the commit and push, and refreshes the same PR.

## Details

The actual URL is required. The Action preserves its Tool-call input/result/effect/report references on its parent Action Run. It does not create another PR, guess a URL, merge, or replay an unknown remote outcome.
