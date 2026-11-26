---
atom_family: TKT
atom_id: AN-T-3968
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: done
  version: 1
  updated_at: '2026-11-26T05:13:50.810810Z'
---

## Summary

Merge the Meta-ontology and Spec Engine into amm/dev

## Objective

Integrate the completed work from AN 1 and AN 2 into `amm/dev`. Preserve MCP port `7777`, supported runtime behavior, and Spec and Ticket history that can coexist with the incoming revisions.

## Scope

- AN 1 handed off nine prepared commits on `efe64b5122`. They include Spec Engine C75 and its consumers, 30 exact Spec Drafts, and the targeted MCP, lifecycle, projection, Manifest Summary, and Workbench fixes.
- AN 2 handed off five prepared patches from `518f61e8e9`. They cover CCE retirement, the typed Node parser, the approved cross-Component Spec changes, and the Project Model carriers. Complete the scoped runtime ports and canonical carrier move in its plan.
- Preserve the target’s pending-graph SQL and Package entry repairs. Keep paused incremental dev-local startup and unapproved work outside this Epic.

## Work

1. **Integrate the prepared changes.** Rehearse the commits and patches on the current `amm/dev` tip. Complete typed Model compilation and startup, lifecycle, Lens groups, and Structure updates. Keep the Lean checks, diagnostics, and last accepted Model behavior.
2. **Reconcile the canonical carriers and records.** Keep the incoming Ontology Score at C82 and assign API Mixer a free ID. Preserve C9 and C58 identities and exact archives. Rebase conflicting Spec Drafts, resolve exact pins and Ticket ID collisions, and preserve pending operator decisions and Draft statuses.
3. **Verify and release.** Compile the bundled and Project Custom Model, check Structure and the Realization Graph, and run the affected lifecycle, Spec Engine, and Workbench tests. Run Local Release and verify MCP on `7777`.

## Working rules

- Use the incoming ontology, Manifests, Contracts, and Solutions where the worktrees disagree. Keep the merge within the two handoffs.
- Commit and push to `amm/dev` after each completed task.
- Resolve unclear decisions against the Operator’s last 24 hours of instructions from this thread, AN 1, and AN 2, then the Project’s Axioms and Applicable Principles. Record a remaining Issue or Question.
- Try to fix MCP when it fails. Use in-place editing or manual carrier creation when the MCP fix is substantial.

## Acceptance

There is one Current carrier per Atom ID and one declaring Manifest per Model address. Exact pins resolve, the target retains its supported behavior, and the full Local Release passes on `7777`. Every completed task has a commit on `amm/dev`.

## Handoffs

- [AN 1 merge plan and nine-commit bundle](/Users/am/.bb/thread-storage/thr_8zxi7bmrvv/amm-dev-session-handoff/merge-plan.md)
- [AN 1 verification](/Users/am/.bb/thread-storage/thr_8zxi7bmrvv/amm-dev-session-handoff/target-verification.md)
- [AN 2 integration plan and five patches](/Users/am/.bb/thread-storage/thr_86zjijbcaj/amm-dev-ontology-integration-plan.md)

## Verification

The merged Model and Structure compiled, exact Spec pins resolved, and all Local Release gates passed. Version 0.4.4.76 is live on port 7777. [AN-T-3971](AN-T-3968-EPIC--merge-the-meta-ontology-and-spec-engine-into-amm-dev/done/AN-T-3971-TASK--verify-and-release-the-merged-stack.md)
