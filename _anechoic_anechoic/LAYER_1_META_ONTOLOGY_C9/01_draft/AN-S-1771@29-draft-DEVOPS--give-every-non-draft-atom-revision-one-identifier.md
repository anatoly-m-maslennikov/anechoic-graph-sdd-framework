---
atom_family: SPEC
atom_id: AN-S-1771
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: draft
  version: 29
  updated_at: 2026-11-05 22:19:14 +0400
---
## Summary

Give Every Non-Draft Atom Revision One Identifier

## Claim

### Prose Claim

For each canonical Atom ID, at most one Current Atom source may exist across all admitted Status values. Every Current or Archived Atom version is identified by exactly one canonical Atom ID and numeric `version`; no second `identifier` field is admitted. Archived versions retain that canonical ID at distinct Version Numbers.

Draft markers are defined by [CA-D-378@30-draft](CA-D-378@30-draft-CORE_META_MODEL-DECISION--serialize-assigned-atom-identities.md), and Draft filename assembly is defined by [CA-D-650@15-draft](CA-D-650@15-draft-CORE_META_MODEL-DECISION--serialize-numbered-version-qualified-draft-atom-filenames.md). Those markers do not change the Current-source uniqueness rule.

An admitted status edit does not create a second concurrent Draft Carrier. [CA-R-1432@28-draft](../../04_requirement/draft/lifecycle-in-place-edits/CA-R-1432@28-draft-CORE_META_MODEL-RULE--govern-atom-lifecycle-identity-and-version.md) governs semantic operation and Version outcomes; [CA-R-1788@19-draft](../../04_requirement/draft/lifecycle-in-place-edits/CA-R-1788@19-draft-CORE_META_MODEL-RULE--initialize-version-creation-timestamp.md) governs timestamps; [CA-D-568@20-draft](lifecycle-in-place-edits/CA-D-568@20-draft-CORE_META_MODEL-DECISION--bind-draft-identity-continuity-evidence.md) governs historical-ID retention.
