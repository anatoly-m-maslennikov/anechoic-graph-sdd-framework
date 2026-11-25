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
  - AN-S-3044@52-draft
  - AN-S-3366@4-draft
  - AN-S-3338@23-draft
  - AN-S-3308@2
  - AN-S-3375@2
  - AN-S-3184@2
  - AN-S-3065@31-draft
  - AN-S-3067@36-draft
  - AN-S-3375@3-draft
  - AN-S-3184@3-draft
  - AN-S-3376@3-draft
  - AN-S-3306@3-draft
  - AN-S-3191@6-draft
  - AN-S-1971@1
  - AN-S-1955@11
  - AN-S-3088@21-draft
  - AN-S-3186@5-draft
  - AN-S-3315@5-draft
  - AN-S-3090@11
  - AN-S-3091@9
  - AN-S-3059@54
  - AN-S-3059@55-draft
  - AN-S-3185@14-draft
  - AN-S-3371@3-draft
  - AN-S-3047@29-draft
  - AN-S-3305@3-draft
  - AN-S-3377@3-draft
state:
  status: archived
  version: 15
  updated_at: '2026-11-25T15:35:41+00:00'
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
Component-target effects. Each has a scoped check. The findings
identify the exact calls and results verified.

C46 uses the C21 Workbench HTTP View Run route. The route,
operation and completed query-ID outcome match the C21 Draft
Manifest, Contract, and Solution. C46 fetches the result page
after receiving the ID and reports a missing ID as an error.
Allowing the missing-ID reply to reach success conflicts with
the C46 Draft Contract. The C43 display outcome and C21 shared
Beta Tool call still match their providers.

For a partial save, C21 returns the completed query ID and save
error, and C46 displays the save error and the result. The
partial outcome and both response effects match the provider
Specs. Omitting the save error from the provider or browser
workflow conflicts with their partial Contracts.

Exact payload values, downstream Backend routing, and the query
ID value used for fetching the result remain open.

For C62 → C66, the `compiler_worker` interface, in-process transport,
and entry `ORCHESTRATOR_C66__shared.Orchestrator.run_worker` match
the provider Manifest, Contract, and Solution. A changed provider
Solution entry produces a conflict in that comparison.

C62 requires the completed C66 Worker outcome. C66 reaps the
process before recording completion. On timeout it kills and
reaps the process before recording the timeout. A terminal record
before reap conflicts with the C66 Draft Contract.

C62 verifies the compiler attestation and shared Model fingerprint
before it accepts and publishes the initial artifacts. Skipping
either check conflicts with the initial-generation Contract.

Structure refresh uses the same Worker binding. Completion and
timeout match the C66 Draft Specs. C62 verifies the replacement
against the admitted Model before publication. Worker or validation
failure retains the previous snapshot. Publishing on failure or
before fingerprint verification conflicts with the refresh Contract.

C66's status route returns active runs and the latest terminal run
for each kind. Starting a Worker as part of a status request
conflicts with that Contract.

C45 forwards the native Backend's status request to C66. The
route, operation, and both lists match the C66 Draft Manifest,
Contract, and Solution. Omitting the terminal runs conflicts
with C45's status Contract. The existing Tool API query check
retains the same facts. Exact instance ID and response values
remain open.

Exact argument and fingerprint values, status record selection,
and Model restart behavior remain open.

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

For C21 → C70, the shared Beta branch requires a raw Tool result
from the shared Workbench API after `POST /tools`. The route and
outcome match the provider's Draft Manifest, Contract, and Solution.
Changing the provider result effect produces a conflict. The C70
rebuild still matches the declared C68 route.

Exact Tool arguments, context, result values, and pinned Project
API outcomes remain open.

For C50 → C53, the Draft Specs pin the in-process
`FEATURE_MODEL_VALIDATION__shared.open_admitted_model` entry and
the opened Model outcome. Both match the provider Manifest,
Contract, and Solution. The C50 Draft opens the Model, selects
the Project Manifest, and compiles in that order. A different
result effect conflicts with the open-path proof.

C53's proposed-instance validator keeps its separate Contract
profile. The exact Model input and returned representation stay
open. The published C50 CLI declaration still matches its Draft
Contract and Solution. The Draft CLI arguments, stdin and stdout
remain unresolved for the additional compiler modes.

C45 sends the native query through the C59 database API at
`POST /database`. The route binding matches the C59 Draft
Manifest, Contract, and Solution. The provider's unsaved query
retains the result before delivery. Its foreign-Project path
rejects the binding before statement selection or result writes.
Changing the route or retaining a result after rejection produces
a conflict.

The Tool API query proof preserves the existing facts, and
the C45 Worker Run status checks still match. Saved queries,
request and result values, and their end-to-end identity remain open.
