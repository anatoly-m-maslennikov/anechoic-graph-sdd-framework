---
atom_family: SPEC
atom_id: AN-S-3909
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 12
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Materialize RMED ownership blocks in implementation

# Summary

Materialize RMED ownership blocks in implementation

## Scope

New or materially changed source in the assessed PROGRAMMATIC implementation
boundary, including Tools, Apps, MCP components, workflows, and their owning
modules or units. Vendor code, generated output, frozen fixtures, and legacy
history remain outside automatic editing unless explicitly admitted.

## Claim

To materialize a direct RMED-to-implementation trace, resolve current
applicable authority first and write one header comment for each directly
implemented Requirement, Evaluation, Delivery, or non-Policy Method (Solution or Decision). Each
comment contains only that Atom ID and Version. Do not cite generic coding
Policies merely because they guided the implementation, or an Atom only called
by the implementation.

## Details

Place the comments before the module's first code. A narrower set may also
appear before an identifiable owning unit when useful. Use the file language's
comment syntax:

```text
# CA-R-2117@13
# CA-M-466@5
# CA-D-674@8
```

Use one Atom per line. Do not add role labels, prose, headings, or an
`implementation of` marker. Preserve the implementation and report a trace gap
when current source cannot resolve, a citation is stale or malformed, or the
owner cannot be identified. Do not invent authority or silently edit excluded
files. The trace does not itself assert conformance, test success, release
readiness, or completion.
