---
atom_family: TKT
atom_id: AN-T-3469
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-23T23:07:47.000000+00:00'
---
## Summary

Specify the carrier body Adapter as a Lean Solution

## Work

Prepare and verify the formal inputs for C30's `carrier_body__pub.py` module:
the existing C30 Adapter Manifest AN-S-3069, the Adapter Contract, and one
planned Tier 1 Adapter Solution. Extend the manifest's formal boundary
declarations for this scope. Add the Contract Formal Claim and an independent
Tier 1 Solution Formal Claim. Derive Lean output where the existing Spec Engine
path supports it.

Use only formal blocks from those three artifacts. Keep pinned Python with Code
Analysis as implementation-side input. Treat source, symbol, and revision pins
as binding evidence.

AN-S-3069 already declares the code and `state: local`. The Contract Formal
Claim adds allowed input bytes, delimiter handling, exact body preservation,
and explicit errors. Each claim covers only
`frontmatter_bounds` and `source_body` in `carrier_body__pub.py`.

The manifest boundary is code access from Python calls, shared-API exports,
explicit byte/path inputs, return/error behavior, and scoped module purity.
The caller owns the host process. The wider C30 boundary owns filesystem
read/write. Record gaps when notation is unavailable.

## Acceptance

Check the intended model in Lean and record unsupported parts of either Formal
Claim or the Lean path. Keep purity scoped to this module.
