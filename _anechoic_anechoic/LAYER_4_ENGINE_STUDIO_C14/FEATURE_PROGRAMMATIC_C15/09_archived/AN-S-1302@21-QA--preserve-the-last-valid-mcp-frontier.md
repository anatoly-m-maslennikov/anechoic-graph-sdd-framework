---
atom_family: SPEC
atom_id: AN-S-1302
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:34 +0400
---
## Summary

Preserve the last valid MCP frontier

## Claim

### Prose Claim

#### Claim checked

one invalid MCP frontier refresh preserves the preceding complete valid frontier
bytes for recovery **and** reports the invalid active Tool **without** presenting
that previous frontier as current.

#### Test case

start with one valid exposed Tool frontier, **then** refresh from a candidate set
containing one active Tool with a colliding endpoint identity.

#### Acceptance criteria

pass **only** **when** the candidate frontier is rejected, the collision is reported,
**and** the preceding frontier bytes remain unchanged for recovery. no new
current registry is published **and** the preceding registry is **not** presented as
current, under CA-R-1110; byte retention alone does **not** authorize call admission.

#### Failure disposition

reject the refresh path **until** replacement is atomic at the validated frontier
boundary.

#### Sources

- [CA-M-193 — Supply the active Tool frontier to MCP](../05_method/CA-M-193-PROGRAMMATIC-ENG_DECISION--supply-the-active-tool-frontier-to-mcp.md)
