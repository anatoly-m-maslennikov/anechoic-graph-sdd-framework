---
atom_family: SPEC
atom_id: AN-S-3292
container:
  component: C63
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "active"
  version: 1
  updated_at: "2026-11-21T20:40:14.364565+00:00"
---

## Summary

Run Local Release from the command line

## Guarantee

From the Framework checkout, append `local --run-id <id>` to the host `uv` command in AN-S-3288. The command enters `LAYER_5_FRAMEWORK_DELIVERY/release.py`. The command accepts `--project-root <path>` and `--image-mode refresh|existing`. It defaults to the Framework checkout and refresh mode. The compatibility option `--test-module` does not narrow a Local Release gate.

A completed request delivers the verified Framework, runtime, and project-local Skill and returns a ready Project MCP endpoint. A candidate that fails verification leaves the running production container in place. On failure, the result gives the failed step and available evidence. Git checkpoints and a candidate Version can already exist when a later step fails.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome, including a failed request or cleanup pending. Exit 2 means invalid CLI usage. Exit 130 means interruption.

## References

AN-S-3290@1, AN-S-1976, and AN-S-1994.
