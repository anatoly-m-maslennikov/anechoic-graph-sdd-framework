---
atom_family: SPEC
atom_id: AN-S-3460
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-09 16:24:06 +0400
---
## Summary

Retain generation, command and release proof

# Summary

Retain generation, command and release proof

## Scope

The evidence that one runtime execution belongs to one activated package and target context.

## Claim

the INSTALL_TOOLS facade **must** bind every runtime process observation to state generation, command and package release proof, and **must not** accept a PID-only assertion as execution identity.

## Details

`.anechoic_runtime/installation/generations/<state_generation>/release-proof.toml` contains package manifest SHA-256, `framework_version`, version carrier SHA-256, source catalog SHA-256, Full Gate receipt SHA-256, immutable image digest, target context SHA-256 and selector SHA-256. `command.toml` contains command SHA-256, exact package-relative argv, environment digest, wrapper digest, state generation and invocation nonce. `process.toml`, if present, contains a transient PID only beside those immutable bindings and observed start token.

The generation directory is written under CA-D-603 and retained across a later generation. A process observation with a changed selector, command, package, context or generation is stale even when its PID remains live. No process record grants selector publication, migration cleanup or retry authority.
