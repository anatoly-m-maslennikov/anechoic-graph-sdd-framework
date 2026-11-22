---
atom_family: TKT
atom_id: AN-T-1417
container:
  atom: AN-T-1418
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Verify Project boundary refusal

## Objective

Independent tests prove cross-Project paths are refused without rejecting ordinary lookalikes.

## Details

Estimated own work: up to 15 minutes. Split further work before exceeding this bound. Inherit the parent's accepted source, independent review and execution gates. Root owns Plans and Git; assigned file ownership stays disjoint.

Prepare fixtures independently while implementation proceeds; final acceptance waits for P2321/P2322. Cover both path fields, foreign roots/descendants, same-name distinct Project instances, missing foreign Structure, owning paths, empty lookalikes, absent paths, malformed/conflicting/symlink/unreadable Settings, and Settings introduction/change/removal. Verify actual Selection, Structure, Graph, Scope and complete-carrier callers and no write effects.

### Definition of Done

The Plan is **not** Done if its stated outcome lacks exact source/code/test evidence and independent verification; required checks fail; a deferred policy is inferred; existing safety checks are bypassed; or source-only/isolated evidence is represented as live runtime or migration acceptance.

### Acceptance — 2026-10-13

The final helper and affected callers passed independent connected-code review and 22 independent boundary tests. Regression results: Graph 36, Structure 23, Scope 12 and full Atom validation 344 passed. Source selection retains original marker/absence evidence; changed markers refuse and reconstructed late handlers cannot reseal missing proof. Exact final pins and scope are in `.anechoic_anechoic/_projection/core-entity-review/stage2/tools-first/declaration-boundary-consumers-acceptance.md`. Settings logical Revision evidence and installed MCP/runtime acceptance remain separate.
