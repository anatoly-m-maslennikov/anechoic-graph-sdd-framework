---
atom_family: SPEC
atom_id: AN-S-3877
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 21
  updated_at: 2026-11-07 13:19:43 +0400
---
## Summary

Regenerate one MCP registry deterministically

# Regenerate one MCP registry deterministically

## Applicable when

Every local release and image rebuild, before the MCP server starts.

## Procedure

Generate the runtime registration asset from the installed code-owned provider inventory and canonical provider descriptors. Derive typed schemas from their code models, validate names and descriptors, and write deterministic output inside the package before its final identity verification. The image build regenerates the same asset from its copied engine code. Do not read native Atoms or call a capability during generation.

MCP loads that generated asset on startup. A source Atom edit does not change exposure or require a generic call-time source catalog scan. Replacing a running implementation follows the existing explicit restart or optional hot-reload boundary; hot reload stays disabled by default.

The actual tools/list export after readiness is a separate discovery output, not the executable registration input.

## Outcome

Equivalent installed code and inventory produce equivalent registration bytes. Build failure stops delivery before startup; invalid individual descriptors retain the existing attributable diagnostics.

## Failure or stop

Report unresolved code/configuration, duplicate identities, invalid generator output or generation failure. Do not rebuild registration from Atoms as a fallback.
