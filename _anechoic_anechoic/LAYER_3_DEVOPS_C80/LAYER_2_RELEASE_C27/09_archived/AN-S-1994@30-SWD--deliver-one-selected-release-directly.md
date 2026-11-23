---
atom_family: SPEC
atom_id: AN-S-1994
container:
  component: C27
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 30
  updated_at: "2026-11-22T12:02:07.787915+00:00"
---

## Summary

Deliver one selected release directly

## Claim scope

The direct Local release path from checked-in assets through package installation, runtime/Skill verification, and Docker/MCP smoke.

## Claim

### Prose Claim

The Tool commits pending nonignored changes under existing protections, bumps and commits the candidate Version, and invokes the single C19 Test Suite entry for the configured functional tests and static checks. After that gate passes, it reads checked-in assets and prepares the retained governed Framework, runtime and `ca` Skill package and builds one immutable candidate image. It invokes the same entry in end-to-end mode against that exact image, then invokes the same entry for a disposable canary before production. After both pass, it installs verified files, starts the exact candidate on the Project-owned Manifest `project_mcp.http_port`, verifies readiness, and applies the production tag to the same image ID. It stops on failure and reports observed effects without automatic replay. Public Release prepares drafts without running a suite.

## Details

As the first Local release step, commit all tracked changes and untracked nonignored files allowed by existing file-safety exclusions, then verify a clean worktree and index. Preserve ignored files and environment-file exclusions; excluded nonignored dirty files stop release rather than being committed or waived. A clean repository is a no-op; commit failure or residual tracked/nonignored untracked changes stop before tests, image preparation/build or Docker work. Before each later Local release step and at completion, inspect Git state and verify cleanliness after its checkpoint. Preserve the project's runtime configuration and do not modify authoritative sources during delivery. Enumerate accumulated Project-owned release containers and images, proving exact ownership and noncandidate immutable identity rather than inferring them from tags or version age. Remove eligible stopped obsolete containers before MCP startup; after successful installation and smoke, repeat and remove obsolete images unused by any container or protected reference. Preserve the exact admitted candidate and one verified previous image for rollback. Preserve running containers outside the existing exact-prior MCP replacement path, unrelated resources and targets with unknown ownership/code identity. Retain and report unproven orphans and cleanup failures; never force-delete or prune globally.

For fresh local-release image builds, attach and inspect exact Project ownership, canonical Project name and full owning-repository build-time Git HEAD commit labels under CA-D-562; refuse fresh preparation when name or HEAD is unavailable or invalid. Docker build cache may be reused without a new ownership claim for reused layers. Use matching inspected exact ownership labels to identify eligible labelled orphans; preserve legacy unlabelled or unproven images. Name and HEAD are provenance only, not cleanup ownership gates: use inspected complete Project ownership and exact immutable identity for retirement. Fingerprints validate runtime classification and source correspondence, not an extra retention slot for another rebuild.

Prepare canonical version/build-date/digest naming after the functional gate passes. Use the candidate tag role `test` for Current and `beta` for Beta. Apply the production tag only after exact-candidate production readiness. Bind retention to that release's exact candidate, not host-clock ordering. Before startup, the existing exact-prior MCP replacement path may replace a positively identified selected-Project container whose image differs from the candidate even when fingerprints match; accumulated cleanup never stops other running containers. After exact candidate launch and smoke verification, inspect selected-Project runtime images and all container references, removing eligible noncandidate digests individually without force. Preserve other Projects' images and unknown ownership even when a selected-Project container formerly referenced them. Retained references or failed inspection/removal remain visible as pending cleanup.
