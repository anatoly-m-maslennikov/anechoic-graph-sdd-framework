---
atom_family: SPEC
atom_id: AN-S-1977
container:
  component: C27
tier: 6
context:
  lens: DevOps
state:
  status: "active"
  version: 22
  updated_at: "2026-11-22T06:18:54.064487+00:00"
---

## Summary

Carry project-owned Docker image cleanup

## Claim scope

Direct Docker/MCP smoke for the installed project runtime and cleanup of superseded project-owned images.

## Claim

### Prose Claim

After the functional gate passes, exact-image end-to-end tests, a disposable canary and successful installed candidate readiness, delivery retains the exact admitted candidate of the current package Version and one known-good previous Project image, when available. It removes other eligible images only when they are positively identified as owned by the selected Project and unused by any container. It never prunes broadly, removes an unrelated image, or forces container deletion.

## Details

Canonical image names carry the exact framework Version, actual Docker build date in UTC and digest suffix; they never replace immutable admission or establish ownership. Ownership requires matching inspected Project identity, host Project root and control root together with positive runtime schema/fingerprint classification; a container link is insufficient. Use actual prior runtime evidence to select the rollback image. Matching Version or fingerprint alone does not earn retention. Preserve other Projects' images, unknown or conflicting ownership and every container reference, including stopped containers. Report the exact kept candidate, removed IDs and retained reasons with truthful pending failures; never force, prune or retry uncertain effects. Build output alone does not prove a working runtime.
