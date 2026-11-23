---
atom_family: SPEC
atom_id: AN-S-131
container:
  component: C16
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Evaluate one sealed Atom identity migration

# Evaluate one sealed Atom identity migration

## Test case

Given identityless legacy, existing-ID correction, duplicate-ID repair, **and** same-path relation/frontmatter-update temporary active Atom carriers with complete sealed requests, evaluate `MIGRATE_ATOM_IDENTITY` dry run twice per request. Both receipts **must** be byte-identical, name the expected source **and** result digests, list **only** declared changes, omit derived `atom_id` **and** `tier`, **and** report no Journal **or** Git effect.

Verify direct `--apply` is rejected **without** authorized project-local MCP delegation. Verify an authorized MCP delegation applies **only** the sealed migration, returns the deterministic receipt, **and** receives durable `COMMIT_TRIGGER` intake acknowledgement **without** a Journal append, staged file, **or** Git commit. Failure cases for source digest, version, duplicate target, occupied destination, old identity, **and** relation target leave **every** carrier unchanged.

## Sources

- [CA-R-1048 — Migrate one sealed Atom identity](../../../306_FEATURE_TOOL_WORKFLOWS/04_requirement/CA-R-1048-TOOL_WORKFLOWS-RULE--migrate-one-sealed-atom-identity.md)
