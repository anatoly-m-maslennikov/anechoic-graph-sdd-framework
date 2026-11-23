---
atom_family: SPEC
atom_id: AN-S-1849
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject an unsealed or unacknowledged Atom mutation

# Reject an unsealed or unacknowledged Atom mutation

## Claim checked

MCP delegates an Atom mutation **only** with one authorized Initiative **and** returns success **only** from the canonical Tool's acknowledged outcome.

## Test case

Submit one mutation request with a missing Initiative, **then** a request whose canonical Tool returns an unacknowledged result.

## Acceptance criteria

Both requests fail explicitly; MCP neither resolves a target nor reports success.

## Failure disposition

Reject the MCP mutation boundary **and** retain the canonical Tool as the operation owner.
