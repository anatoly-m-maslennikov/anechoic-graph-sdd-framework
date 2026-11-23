---
atom_family: SPEC
atom_id: AN-S-66
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject a custom Git Hooks path conflict without mutation

# Reject a custom Git Hooks path conflict without mutation

## Claim checked

Installing the managed Git Hooks fails safely **when** the repository already declares another local `core.hooksPath`.

## Test case

Prepare a repository with a custom local `core.hooksPath`, executable Hook carriers **and** recorded bytes **and** modes, but no managed ANECHOIC Git Hook registration; invoke `INSTALL_TOOLS run --apply`.

## Acceptance criteria

Installation returns one stable conflict diagnostic. The configured path, **every** referenced Hook byte **and** mode, adapter registry, Git configuration, index, refs, `.anechoic_runtime/tools`, **and** `.anechoic_runtime` remain unchanged, **and** no backup carrier is created.

## Failure disposition

Reject the delivery **if** installation replaces, merges, copies, backs up, **or** partially registers over the custom Hook configuration, **or** **if** the failure is **not** deterministic.
