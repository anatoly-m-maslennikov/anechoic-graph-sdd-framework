---
atom_family: SPEC
atom_id: AN-S-1934
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: "active"
  version: 6
  updated_at: "2026-11-23T01:48:06.183836+00:00"
---
## Summary

Verify code-owned MCP registration without Atom discovery

## Claim

### Prose Claim

Verify Backend generates equivalent registration bytes for equivalent installed provider inventory and descriptors. Check add, remove and changed descriptors, duplicate names, invalid entries, exclusions and unavailable providers. Verify valid entries remain available when an unrelated entry is quarantined.

With registration-time Atom reads made to fail, verify Backend catalog discovery and a code-only Tool call work; unrelated Atom edits do not change exposure. Operations still enforce their own business prerequisites.

Verify refresh and existing delivery modes, package and image identity, and failure before startup when generation or verification fails. Compare the MCP `tools/list` output with Backend's enabled catalog. Exercise equivalent MCP and web calls, including single and shared Project binding, rejection, cancellation and result/error semantics. Confirm MCP adds no business implementation and uses the Backend JSON bridge.
