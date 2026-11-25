---
atom_family: TKT
atom_id: AN-T-3924
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 24
  updated_at: '2026-11-25T18:37:09+00:00'
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

The C68 Draft Manifest now also requires the replacement ID
effect. The Manifest, Contract, and Solution match the C70
requirement. Exact field types and which IDs correspond to each
requested result remain open.

C68 sends full admission to C71's `PUT /generation` route after
receiving the sealed snapshot. C71 verifies the inputs before
committing. Failed admission retains the previous generation.
The route and both outcomes match the C71 Draft Specs. C68
returns replacement IDs only after commit. Skipping the receipt,
the commit, or retention produces a conflict.

Exact receipt and result values, transaction atomicity, and the
Structure representation remain open.

For a lifecycle write with a recorded outcome and carrier delta,
C68 calls C71 at `PUT /generation/native-delta`. The Draft route
and commit, stale-base, and reconciliation outcomes match.
C68 reports the recorded write outcome even when projection is
rejected. C71 retains its previous projection on rejection.

Five deliberate changes to the Draft workflows conflict with the
Contracts. Exact base and write-outcome values, transaction
atomicity, and lifecycle serialization remain open.

For C70 → C68, the lifecycle request matches the jobs interface and
`POST /jobs/lifecycle` route. C70 preserves three separate outcomes.
A lost Worker reply yields an unknown write result and blocks later
writes. A known write with a failed projection retains its recorded
result. A blocked request stops before Worker dispatch.

Lean detects five violations, including a repeated write after a
lost reply and a dispatch while blocked. The Contract states that
complete snapshot admission lifts the block. The proof covers
individual requests; the lifetime of the gate across requests and
the exact reply values remain open.

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

C68 now requires a C69 lifecycle result before submitting a native
delta to C71. The C69 result carries a recorded write and a carrier
delta verified against the write receipt. C69 reports a projection
error without returning a successful delta. Lean detects an
unchecked delta, a successful delta after projection failure, and
submission without the Worker result. Exact payload identity and
the Orchestrator path for a Worker projection error remain open.

C68 reports a C69 projection error received without a checked delta.
The error matches the C69 Draft Manifest, Contract, and Solution.
Lean detects submission to C71, repeating the write, or suppressing
the error on this path. Exact write effects carried with the error
and the corresponding C70 response remain open.

C70 receives the C68 Worker projection error and reports projection
failure. The call and error match the C68 Draft Manifest, Contract,
and Solution. Lean detects a suppressed error, a refusal in its
place, and a report without the C68 error. The exact file effects
and response payload for this case remain open.

For Incremental Startup with changed Current or Draft carriers,
C68 observes the C71 checkpoint proof. The selected outcome
matches the C71 Draft Manifest, Contract, and Solution. Lean
rejects missing base confirmation, commit, or current proof. It
also rejects exposing the proof before the commit. Exact values,
transport, and the unchanged and cold startup cases remain open.

C65 calls the C27 Release entry point for build-image and run-image.
Each command matches all three C27 Specs. Lean detects a wrong
command and a launch requested before the build returns.
Exact run flags, image identity and result values remain open.

Setup selects apply and MCP verification on the C27 run-image call.
Both settings scopes require the C81 verified outcome. The flags and
outcome match the C81 Draft Manifest, Contract, and Solution through
the checked C27-to-C81 dispatch. Lean rejects a skipped, early, or
unrequested probe and applying a plan-only request. Exact image,
settings and response values remain open.
