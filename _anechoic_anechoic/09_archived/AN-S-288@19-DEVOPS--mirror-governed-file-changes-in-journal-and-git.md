---
atom_family: SPEC
atom_id: AN-S-288
container:
  component: C00
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Mirror Governed File Changes in Journal and Git

# Mirror Governed File Changes in Journal and Git

**when** the Git Extension is selected, materialize **every** approved atomic change set as follows:

- create **`=1`** Git Commit containing **all** **and** **only** the approved changes; the change set **may** contain **`>=1`** File Carriers.
- retain **`=1`** canonical Journal file-change Event for **every** changed File Carrier, including **every** successor **and** predecessor Carrier changed by replacement.
- preserve the correspondence between the committed change set **and** its individual Journal Events; Git **must not** become another authoritative Journal.

successor **and** predecessor Carrier changes **may** share the approved atomic change set. their individual Journal Events **must not** require separate Git Commits.
