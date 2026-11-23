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
  status: "archived"
  version: 2
  updated_at: '2026-11-21T21:49:45.763566+00:00'
---

## Summary

Run Local Release from the command line

## Guarantee

From the Framework checkout, append `local --run-id <id>` to the host `uv` command in AN-S-3288. The command accepts `--project-root <path>` and `--image-mode refresh|existing`.

It defaults to the Framework checkout and refresh mode. The compatibility option `--test-module` does not narrow the Local Release gate.

C63 imports no Project code outside the Release subtree. Its only subsystem calls are to the C19 Test Suite command interface, for `unit`, `e2e`, and `canary` phases. It uses the host Git and Docker operating-system interfaces directly.

C63 reads Project Manifest literals and the checked-in registry, copies active sources, builds the exact candidate image, and installs the verified package. It starts and checks the production container directly through Docker.

It writes its own release receipts and does not call Journal.

A completed request delivers the verified Framework, runtime, and project-local Skill and returns a ready Project MCP endpoint. A candidate that fails verification leaves the running production container in place.

A failure reports the failed step and available evidence. Git checkpoints and a candidate Version can already exist when a later step fails.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome, including a failed request or cleanup pending. Exit 2 means invalid CLI usage. Exit 130 means interruption.

## References

AN-S-3290@2, AN-S-1976, and AN-S-1994.
