---
atom_family: SPEC
atom_id: AN-S-2813
container:
  component: C16
tier: 1
context:
  lens: SWD
state:
  status: draft
  version: 1
  updated_at: 2026-10-23 18:22:28 +0400
---
# Summary

Separate Tool module responsibilities

## Scope

The agreed TOOLS module partition for new or changed PROGRAMMATIC Tool design.

## Claim

Keep TOOLS as one modular runtime with shared queue and run state under
CA-M-432. Partition responsibility into:

- `ADAPTERS`: backend access, including governing Configuration.
- `SINGLE_ACTIONS`: target-specific operations.
- `SCHEDULERS`: batch and Workflow scheduling driven by recorded results.
- `ACTION_ENGINE`: queue consumption, execution, and result recording.

Tool Workflows (C18) own concrete Workflow sequences under AN-S-2481@25.

## Details

These are responsibility boundaries inside one modular runtime, not service
boundaries. Do not introduce microservices for them or add a separate prompt
helper for Find+Fetch. Project-specific Tools use the same responsibility
classification rather than a special umbrella. Existing contracts are not
relocated by this Method, and this Method makes no runtime-completion claim.
