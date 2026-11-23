---
atom_family: SPEC
atom_id: AN-S-2364
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Seal a stable Event source snapshot before query execution

# Summary

Seal a stable Event source snapshot before query execution

## Scope

The query-source snapshot.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** bind an immutable source snapshot before
workflow/action-start execution evidence can append and must not enlarge that
snapshot with its own execution Events.

## Details

The token binds the source root, raw-Journal byte-prefix length and hash, ordered
member references, member byte hashes and actually supplied string Event IDs,
without deduplication or a unique-ID requirement. Capture all decoded rows,
including rows without a string ID; preserve their recorded JSON unchanged.
Before every
continuation it revalidates the source/prefix hashes and captured members:
changed, deleted, unreadable, or truncated members reject continuation; bytes
appended only after the sealed prefix do not. An unavailable, changed, or
incomplete frontier cannot claim complete coverage.
