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
  status: active
  version: 9
  updated_at: '2026-11-23T14:45:10.920666+00:00'
relations:
  ANSWERS:
  - AN-S-3290

---

## Summary

Run Local Release from the command line

## Guarantee

Use `local --run-id <id>` with the host command in AN-S-3288. Local Release
checkpoints Git, bumps the candidate version, and selects Active source Atoms.
Run Static first and then the required host functional checks before building
the candidate image. `--test-module` leaves both required gates in force.

Use `prepare-local` with an exact base commit, literal changed paths, and
an isolated loopback port to prepare a private checkout for Local Release.
Report its exact revision. Installation belongs to the subsequent Local Release.

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

AN-S-3290 and AN-S-4734.
