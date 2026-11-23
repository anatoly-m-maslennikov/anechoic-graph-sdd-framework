---
atom_family: TKT
atom_id: AN-T-268
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 18:08:27 +0400
---
## Summary

Finalize Version History **with** the verified release PR link

# Summary

Finalize Version History **with** the verified release PR link

## Objective

the AI Agent finalizes the release Version History entry as **only** a concise summary **and** a link to the actual verified PR.

## Details

- input: the verified PR URL/head/base, full public-release description, current Version History, canonical Version **and** exact public gate evidence.
- use **only** the verified PR URL; do **not** guess a PR number **or** treat a placeholder **or** compare URL as the requested PR link.
- **if** a matching existing PR is discovered **before** Task 14's freeze, include its URL there; this Task verifies the final entry **and** can finish as an evidenced no-op **when** the final snapshot already satisfies the contract.
- **if** creating a new PR supplies the URL **after** the first publication, update the entry, obtain a fresh complete public full-suite gate for the changed snapshot, then commit/push the gated follow-up to `amm/dev` **and** refresh the PR's head/description. record the actual Workflow/Step/Action lineage **and** Tool-call evidence; do **not** reuse the pre-link gate for changed bytes.
- the PR carries the full lists of what is new **and** what is fixed, plus migration/test evidence; Version History retains **only** its short summary **and** PR link. preserve the established bullet-point structure.
- this documentation-only link finalization does **not** independently change the already sealed Version **or** claim that `main` has merged.
- own work **must** fit **<=15** minutes; decompose residual work **before** exceeding that boundary.

### Definition of Done

the Plan is **not** Done **if** the entry lacks the verified PR link, duplicates the full change lists, the public PR lacks the full new/fixed lists, a changed final snapshot was pushed **without** its fresh full gate, **or** final commit/PR evidence is missing.
