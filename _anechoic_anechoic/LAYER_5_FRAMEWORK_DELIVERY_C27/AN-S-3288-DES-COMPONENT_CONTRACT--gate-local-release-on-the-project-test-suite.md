---
atom_family: SPEC
atom_id: AN-S-3288
container:
  component: C27
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-21T19:38:49.555642+00:00'
---

## Summary

Gate Local Release on the Project Test Suite

## Guarantee

After committing pending nonignored changes and the candidate Version bump, Local Release invokes the single C19 Test Suite entry once for unit tests and linters. A failure stops before package preparation and image build.

After a green result, C27 prepares the retained governed Framework, runtime and Skill package and builds one immutable candidate image. C27 invokes the same Test Suite entry in end-to-end mode against that exact image, then runs a disposable canary. Either failure stops before production replacement.

After both gates pass, C27 installs the verified files, starts the exact candidate on the Project-owned Manifest `project_mcp.http_port`, verifies readiness, and applies the production tag to the same image ID. It retains the verified previous image when available. Failures report observed effects without automatic replay.

Public Release retains its full-suite behavior.

## References

AN-S-1976, AN-S-3287, AN-T-2944, and AN-T-2958.
