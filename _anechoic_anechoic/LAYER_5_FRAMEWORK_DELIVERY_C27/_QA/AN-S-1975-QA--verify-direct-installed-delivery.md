---
atom_family: SPEC
atom_id: AN-S-1975
container:
  component: C27
tier: 5
context:
  lens: QA
state:
  status: "active"
  version: 21
  updated_at: "2026-11-22T06:18:53.795333+00:00"
---

## Summary

Verify direct installed delivery

## Claim scope

The installed project runtime and `ca` Skill after a direct Local release.

## Claim

### Prose Claim

The QA case verifies the installed package/runtime and project-local `ca` Skill, then verifies the exact candidate on the Project Manifest port and its readiness. A failed check stops the release and is reported for manual handling.

Check both accepted image modes. Verify that each uses the checked-in assets selected for the release. Missing or invalid required assets stop before tests or image build. Verify that the end-to-end tests and canary use the exact admitted candidate image.

## Details

This case does not require a sealed manifest, a separate full-suite aggregation protocol or promotion state. Verify the exact admitted immutable candidate, package Version and canonical version/build-date/digest tag using the existing runtime evidence.

Use independent synthetic Projects and Docker observations to check: a single C19 entry invocation for configured functional tests and static checks precedes release-image preparation; the same entry in end-to-end mode tests the exact candidate image, followed by a disposable canary before production; failed pre-build tests or preparation cause no production startup or image removal; failed end-to-end tests or canary cause no production replacement; cleanup requires verified exact candidate launch even with no prior image; retain that candidate and exactly one verified prior image when available. An unused, fully selected-Project-owned older rebuild is removable even with the same fingerprint. A same-fingerprint but different-image exact prior Project MCP is replaced by the existing ownership-checked path, while exact candidate reuse remains allowed. Foreign, unowned, incomplete/conflicting ownership, running containers outside that path, and images referenced by any container are preserved. Cover failed observation/removal, pending reporting, no force/global prune and no uncertain retry. These functional checks do not authorize an actual release or production Docker effects.



Verify that the selected Version remains mutable before the authorized release event succeeds and its exact candidate outcome is recorded. Readiness, implementation completion and candidate naming alone do not freeze it. A failed or unrecorded release does not count as the successful release event.
