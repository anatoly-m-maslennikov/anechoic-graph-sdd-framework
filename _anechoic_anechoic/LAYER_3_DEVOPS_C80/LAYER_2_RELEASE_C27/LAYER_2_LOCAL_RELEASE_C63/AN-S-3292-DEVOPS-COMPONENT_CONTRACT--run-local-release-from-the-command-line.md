---
atom_family: SPEC
atom_id: AN-S-3292
concern:
  components:
  - C63
  - C19
  - C21
  - C81
container:
  component: C63
tier: 0
context:
  template: component_contract
  lens: DevOps
state:
  status: active
  version: 9
  updated_at: '2026-11-23T14:45:10.920666+00:00'
relations:
  ANSWERS:
  - AN-S-3290
  IS_REFERENCE:
  - AN-S-4733
  - AN-S-3346@1
  - AN-S-3287@6
---

## Summary

Run Local Release from the command line

## Guarantee

Use `local --run-id <id>` with the host command in AN-S-3288. Local Release
checkpoints Git, bumps the candidate version, selects Active source Atoms, and
runs the static and required host test gates before building the image.
`--test-module` leaves the required gate in force.

Run end-to-end and canary checks on the exact candidate image before installing
the verified package and its `ane` Skill. Preserve authoring sources and
protected configuration. Start the candidate on the Project Manifest port
and tag it as production after MCP is ready.

After promotion, apply the retention standard in AN-S-4733. Report
incomplete cleanup separately from promotion failure.

Report the failed step and observed effects on failure. Write release receipts
under `.anechoic_runtime/simple_local_release/` and test logs under
`.anechoic_tmp/simple_local_release/`.

If Project selection fails before execution, report
`validate_project_selection` and an empty list of effects.

## References

AN-S-3290.
