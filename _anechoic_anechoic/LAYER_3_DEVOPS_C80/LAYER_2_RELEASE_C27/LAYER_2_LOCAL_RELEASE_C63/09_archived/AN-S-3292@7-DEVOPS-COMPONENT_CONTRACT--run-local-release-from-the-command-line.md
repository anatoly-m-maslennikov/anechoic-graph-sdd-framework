---
atom_family: SPEC
atom_id: AN-S-3292
container:
  component: C63
tier: 0
context:
  template: component_contract
  lens: DevOps
state:
  status: archived
  version: 7
  updated_at: '2026-11-23T14:19:08.738894+00:00'
relations:
  ANSWERS:
  - AN-S-3290
  IS_REFERENCE:
  - AN-S-3346@1
  - AN-S-3287@6
---

## Summary

Run Local Release from the command line

## Guarantee

Use `local --run-id <id>` with the host command in AN-S-3288. Local Release
checkpoints Git, bumps the candidate version, selects Active source Atoms, and
runs the static and required functional gates before building the image.
`--test-module` leaves the required gate in force.

Run end-to-end and canary checks on the exact candidate image before installing
the verified package and its `ane` Skill. Preserve authoring sources and
protected configuration. Start the candidate on the Project Manifest port
and tag it as production after MCP is ready.

Keep the current image and up to two prior Project-owned production images.
Purge eligible unused test images and retire proven obsolete Project resources.
Protect resources that containers reference and test images in use by active
releases. Report unverified ownership and failed cleanup.

After successful promotion, target 4 GB of Docker build cache and 2 GB of free
space. Purge temporary files older than 48 hours, preserving shared locks,
managed tool caches, and resumable Atom Review state.

Report the failed step and observed effects on failure. Write release receipts
under `.anechoic_runtime/simple_local_release/` and test logs under
`.anechoic_tmp/simple_local_release/`.

## References

AN-S-3290.
