---
atom_family: SPEC
atom_id: AN-S-4732
container:
  component: C81
tier: 0
context:
  template: component_contract
  lens: DevOps
relations:
  ANSWERS:
  - AN-S-4704
state:
  status: active
  version: 1
  updated_at: '2026-11-23T14:45:10.920666+00:00'
---

## Summary

Build and run runtime images

## Guarantee

Use the Release CLI in AN-S-3288. `build-image --project-root <root> --run-id <id>`
builds from the selected checkout. It returns the immutable image ID, input
fingerprint, and version. It performs no release or installation.

`run-image --image <sha256:id>` prepares the shared MCP launch for an exact
image. Use `--host-settings <path>` to select host settings. Without `--apply`,
it returns the launch plan with no container changes.

With `--apply`, launch through Engine Studio and wait for readiness. The JSON
result identifies the image and readiness outcome. Use `--verify-mcp` with
`--apply` to add an MCP probe before success.

For Local Release, start the selected image for the Project on the supplied
loopback port and return the health-checked MCP endpoint.
