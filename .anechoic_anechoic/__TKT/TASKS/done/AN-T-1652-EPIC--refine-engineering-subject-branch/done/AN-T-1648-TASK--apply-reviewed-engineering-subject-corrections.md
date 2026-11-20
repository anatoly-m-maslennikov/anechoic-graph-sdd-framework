---
atom_family: TKT
atom_id: AN-T-1648
structure:
  container:
    atom: AN-T-1652
  priority: 2
context:
  template: task
state:
  status: done
  version: 3
  updated_at: 2026-10-27 06:19:16 +0400
---
# Summary

Apply reviewed Engineering Subject corrections

## Objective

Review and apply Candidate #9 Drafts, preserving predecessor history and unrelated work.

## Details

Use the decisions in P2667 and actual Drafts from P2668. Review the exact batch before promotion. Verify source identity/version and stop on a changed source or unsuccessful write.

For each accepted update, archive the Current predecessor with its previous Version and promote the next-version Draft. Classification-only path changes preserve the Atom ID. A changed Summary or Content Role requires a new ID. New definitions start with their own IDs. Preserve unrelated content and historical revisions.

Update the thin table from Drafted to Applied only after the corresponding Current source exists and matches the accepted successor. Keep unresolved changes separate.

## Definition of Done

- Applied Current heads and predecessor archives match the reviewed batch.
- Missing definitions are active only after their accepted Drafts are promoted.
- Unresolved cases and actual partial progress are recorded; no unreviewed content is published.

## Completion

Completed in Candidate #9: reviewed Drafts were promoted with predecessor archives; the four Current-source Subject views were rebuilt and checked. See the parent Epic for the applied counts and retained exclusions.
