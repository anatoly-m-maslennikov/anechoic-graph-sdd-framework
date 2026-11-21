---
atom_family: SPEC
atom_id: AN-S-3293
container:
  component: C64
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "active"
  version: 2
  updated_at: "2026-11-21T20:54:47.544610+00:00"
---

## Summary

Run Public Release from the command line

## Guarantee

From the Framework checkout, append `public --run-id <id>` to the host `uv` command in AN-S-3288. The command enters `LAYER_5_FRAMEWORK_DELIVERY/release.py`. Use `--project-root <path>` to select a different Project checkout. Supply `--content-draft <file>` as UTF-8 JSON with a description and a list of summary strings.

Without a content draft, the command returns the required input schema.

To publish, the checkout must have a valid active Project Manifest that declares `parameters.project.repository_slug`. The configured fetch and push origins must resolve to the same GitHub repository with that slug. Invalid or mismatched identity stops the request before staging or writing to the remote.

A completed request publishes the verified release changes to the selected pull request branch and reports the pull request. A failed request reports the failed step and any effects that already occurred.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome, including a request for input. Exit 2 means invalid CLI usage. Exit 130 means interruption.

## References

AN-S-3291@1 and AN-S-2314.
