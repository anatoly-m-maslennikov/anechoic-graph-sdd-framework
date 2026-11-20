---
atom_family: SPEC
atom_id: AN-S-1718
structure:
  container:
    component: C9
  tier: 7
context:
  lens: QA
state:
  status: active
  version: 51
  updated_at: 2026-11-05 22:47:24 +0400
---
## Summary

Validate Atom Scope **and** Claim Scope

## Claim

### Prose Claim

Verify that each complete Atom has exactly one `Header.Subjects.Active` and resolves its target Scope Unit from that active Subject. Containment and the Atom's own Scope context are separate from target resolution. Preserve textual applicability in Claim.Prose Claim without letting it select a different target.

## Details

### Test case

Create valid local and cross-Scope Goal or Demand fixtures with resolvable active Subjects. Include separate containment and own Scope contexts, and narrower and composite textual applicability in Prose Claim. Repeat with a missing, ambiguous, or unresolved active Subject and with applicability that contradicts its resolved target.

### Acceptance criteria

Each valid fixture has exactly one active Subject, resolves its target from that Subject, preserves its applicability, and retains its distinct containment and own Scope context. Each invalid fixture fails and identifies the affected Subject or contradictory applicability. Do not infer another target from applicability or repair an unresolved Subject by guessing.
