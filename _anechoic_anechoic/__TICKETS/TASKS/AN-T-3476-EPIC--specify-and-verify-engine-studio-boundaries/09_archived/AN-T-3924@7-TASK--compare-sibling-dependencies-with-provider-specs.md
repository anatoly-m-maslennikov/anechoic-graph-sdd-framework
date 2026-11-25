---
atom_family: TKT
atom_id: AN-T-3924
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-T-3489
  - AN-S-3380@6-draft
  - AN-S-4732@1
  - AN-S-3088@20
  - AN-S-3379@3-draft
  - AN-S-3315@4
  - AN-S-3316@3-draft
  - AN-S-3383@4-draft
  - AN-S-3338@22
  - AN-S-3340@28-draft
  - AN-S-3385@4-draft
  - AN-S-3337@24
  - AN-S-3339@25-draft
  - AN-S-3363@4-draft
  - AN-S-3060@9-draft
  - AN-S-3372@3-draft
  - AN-S-3044@51
  - AN-S-2547@20
  - AN-S-3337@25-draft
  - AN-S-3334@29-draft
  - AN-S-3336@26-draft
  - AN-S-3384@3-draft
  - AN-S-3290@14-draft
  - AN-S-3292@10-draft
  - AN-S-4704@4-draft
  - AN-S-4732@2-draft
  - AN-S-4879@1-draft
state:
  status: archived
  version: 7
  updated_at: '2026-11-25T14:31:24+00:00'
---
## Summary

Compare sibling dependencies with provider Specs

## Work

Use declared dependencies between sibling Components. Compare the
caller's formal Solution with the provider's Manifest, Contract,
and primary Solution. Check the interface, inputs, guarantees,
outputs, and effects that the caller relies on.

Start with Local Release's dependency on Runtime Images for image
build and launch. Pin both Components' declarations and show which
calling details each source establishes.

## Acceptance

Report a separate verdict against each provider Spec with exact
source links. Distinguish missing call bindings from contradictory
bindings and keep unmodeled guarantees unresolved.

## Findings

The inspected Solution pins include six sibling edges with
Component-target effects. C21 → C70 and C50 → C53 still lack
selected logical operations in their caller claims.

C46 sends `view_run` through the declared C21 Workbench HTTP
boundary. C45 serves native requests downstream. The C46 route
matches the C21 Manifest. Its browser Contract and Solution
profile and Backend operation mapping remain open.

For C62 → C66, the `compiler_worker` interface, in-process transport,
and entry `ORCHESTRATOR_C66__shared.Orchestrator.run_worker` match
the provider Manifest, Contract, and Solution. A changed provider
Solution entry produces a conflict in that comparison.

The call arguments and returned fields remain unresolved. C66 records
Worker completion. C62 separately accepts the Model and Structure
artifacts.

For C70 → C68, `POST /jobs/build` on the jobs interface matches
the provider Manifest, Contract, and Solution. The caller requires
replacement IDs before reporting success. The provider Contract and
Solution require them after Kernel admission. Changing the formal
response effect produces a conflict.

The provider Manifest declares the route and build request fields.
The response effect, exact field types, and which IDs correspond to
each requested result remain unresolved at the applicable boundaries.

For C68 → C69, the managed CLI `atom_snapshot` binding and
sealed snapshot outcome match the Worker Draft Manifest,
Contract, and Solution. The Orchestrator requires the receipt
before Kernel admission. A Worker start followed by an unsealed
result conflicts with that requirement. Exact stdin and stdout
values and parent lifetime behavior remain open.

For C63 → C81, the image build and Project launch outcomes match
the Runtime Images Draft Manifest, Contract, and Solution.
Both Local Release completion outcomes require the built image
and a healthy MCP endpoint. An unhealthy endpoint conflicts
with either outcome.

The Project launch uses the selected image and supplied loopback
port. Concrete call transport, entry point, and exact argument
and result values remain open. The public `run-image` command
retains its independent launch-plan behavior.
