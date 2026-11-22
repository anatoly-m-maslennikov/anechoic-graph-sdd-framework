---
atom_family: TKT
atom_id: AN-T-2976
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 15
  updated_at: "2026-11-22T16:28:47.208860+00:00"
---
## Summary

Evaluate a parallel Beta Backend, Kernel, and Workers stack

## Prerequisite

Complete the MCP bridge under AN-T-2944. MCP maps the Backend JSON Tool catalog, forwards calls, and returns responses.

## Work

- Build Kernel, Orchestrator, Workers, and Backend alongside the current
  stack. Name each Beta Component `<component name>_beta_<new component ID>`.
- Use one `stack` setting in the `LAYER_5_FRAMEWORK_DELIVERY/project.toml`.
  Its value selects `current` or `beta` as a set. Build each selection
  as a distinct image.
- Confirm child Components and Component Seeds with the proposed map in
  AN-T-2958. Add one `__shared` entry Module to each Beta Package with
  direct code. Other Packages may import only that Module, subject to
  Code Access. Give each Seed one Manifest, an ID such as `CS123`, and
  an exact Spec Binding in its implementation Package.
- Inspect existing behavior and adopt the pieces that satisfy Beta's
  Contracts, state ownership, and interfaces.
- Start the comparison with a real Project query backed by Worker-built
  Model and Structure artifacts. Refresh those artifacts after a file
  change. Use identical fixtures and acceptance checks for both images.
- Record discrepancies in either image and evaluate each against the
  applicable Specs and Contracts.

## Outcome

Use the two-image evidence to decide whether to continue with Beta and what corrections each stack needs.

## Verification

Local Release built separate Current and Beta images from the same
selector. Both answered an inline query through MCP and the Web API.
Beta served distinct rows from two Projects on a shared host.

Fresh images ran against identical copies of a Project with a Tier 4
Component Manifest. Both published its initial Structure, added a valid
revision, recorded a failed build for an invalid revision, and recovered
on the next valid edit.

During the failed build, Beta kept both artifacts and the accepted query
row. Current kept both artifacts and exposed the invalid row through its
separate projection path. At that checkpoint the two query schemas used different Summary
column names. In that comparison, Beta exposed one Tool and omitted paging and type metadata.

The comparison of remaining Tool behavior and Contracts continues.

The normal shared launcher started a Beta image with one Backend and
separate Kernel and Orchestrator peers for two Projects. MCP and Web
read the public SQL schema. Queries reused the same peers and a valid
edit refreshed one Project without changing the other. Single-Project
launcher verification passed through the same schema Tool.

The Realization Graph verified one shared entry in each of seven Beta
Packages, two allowed imports between those Packages, and zero denied
or unresolved sites. The static Test Suite passed the 300-line module
limit and the 45-line function limit.

The Beta image returned typed query pages from the owning Kernel and
presented `content.summary` in the public schema. Real MCP and Web
requests passed for run, page, and check. One admission process served
the shared Backend while two Projects reused separate Kernel and
Orchestrator peers. A valid edit refreshed one Project.

The Beta comparison still needs the remaining Workbench operations and
storage settings.

The Beta Worker builds the enabled Realization Graph, and Kernel admits
it together with the matching Project rows, Model, and Structure.
The fresh Beta image published the graph schema by default. After a
source rename, MCP and Web returned the changed resolution while the
other Project kept its own data. A Project can disable the graph.

The Local Release canary passed on the fresh Current and Beta images.
The Beta comparison continues for persisted storage, remaining
Workbench operations, and Component relationships in the graph.

## Paired verification update

Both images passed the Local Release MCP canary. The paired Docker suite
ran 13 cases per image. Current passed 12 and Beta passed 7. The browser
launcher failed in the managed environment for both images.

Beta passed the Realization Graph relation-count queries, including
DuckPGQ MATCH. Its View flow then stopped at an unavailable Tool. The
other differences were Work Journal, native reference and relation
projection, lifecycle Tools, and View execution and rebuild.

Focused tests verified that Beta disk storage reopens the accepted
generation after a failed rebuild. Its property graph remains queryable
after rollback and restart. These checks do not establish Journal parity.

Beta now persists Workspace and View edits in Kernel. MCP and shared
Backend tests verified stable IDs, restart, Project isolation, and
refusal of stale View revisions. View run, fetch, check, and save
still require comparison and implementation.

Chrome launched for a second paired run. Current completed 31 browser
tests before the suite deadline. Its native watcher also missed
the edit latency limit. Beta completed one browser test and six failed
before the deadline. Beta reached View run in the graph scenario
after a successful Workspace open and edit.

## View, Journal, and native projection comparison

Beta supports inline View run, check, and fetch. Kernel manages the
shared result cache and pins results while a View uses them. Journal
queries read the existing Project DuckDB store in either projection
storage mode. Workers build native Atom and relation rows, and Kernel
publishes each accepted generation in one transaction.

Both Current and Beta passed Local Release canaries on two image pairs.
In the first pair's serial Docker E2E comparison, Current passed 11 of
13 cases and Beta passed 4. Current failed shared-runtime readiness and
the browser flow. Beta completed the browser graph scenario through
View execution. Saved queries, rebuild, and lifecycle promotion remain
unavailable in Beta. The browser flow also failed in Beta.

Beta missed the existing deadlines for several code and native Atom
updates. A separate probe confirmed that dependency add and removal
updates eventually appeared. The delay between event detection and
admission still needs measurement. Keep the existing latency checks.

The Realization Graph resolved all observed Python and web sites, with
zero denied cross-Component imports. All 12 Beta Packages passed the
shared entry check. The all-Package migration remains open under
AN-T-2946.

## Grid, rebuild, and file Journal

Beta serves grid-filtered, sorted and grouped pages from Kernel. The
ordinary MCP process verified file-backed Journal queries at an admitted
custom path and a rebuild that replaced the live View result ID.

Orchestrator serializes explicit rebuilds with file changes. Kernel
commits the new generation and retained-result refresh together. Keep
the prior generation and result IDs when refresh fails. The shared host checks status
without starting a cold Project and retains Project isolation on rebuild.

The isolated Beta image probe observed dependency add and removal in
about four seconds. Event detection took under one second. The
remaining delay was Worker build and Kernel admission. The native
Atom watcher still needs verification against its existing deadline.

The Current Journal appender accepts records without a sealed identity.
AN-S-170 requires an identity, digest and receipt across retries. Saved
query parity depends on the shared sealed writer and the identity for
Workbench writes. The checked-out worker and reader do not establish
that guarantee.

Current and Beta passed Local Release canaries after the grid, file
Journal, and rebuild changes. Later MCP and private-socket tests
verified atomic rebuild and settled result IDs. Paired browser
verification then passed 13 of 13 cases on Current and 9 of 13 on
Beta. The two images were tested by immutable ID, and both passed
the Local Release canary. Beta passed the rebuild and shared Project
isolation cases. The saved query and lifecycle promotion operations
remain unavailable. Beta exceeded the native watcher deadline, and
the full browser flow reached its global timeout.

The next Beta revision adds Project-scoped query history. The Kernel
socket test verified expiry, restart, SQL, and exact Run metadata.
Native watcher polling now skips excluded code directories and waits
less between capture and rebuild. The same image test deadline applies.

## Schema and Task lifecycle

The paired query-history images were `sha256:1428f1d6b66b193962b096b75b84cdfa4587ff8cfe5decc882a61d880bbd633b` (Current) and
`sha256:08a429ce0be7fcaff6d389f992efd0011c5913d3685934972f885187936f864c` (Beta). Both passed their release canaries.
The checked-out functional suite for that pair passed 463 tests.
The exact Beta image missed the native Atom watcher create deadline
and retained a stale import status after a populated-directory edit.

Beta now reads public schema and optional Status values from one
accepted Kernel generation. The real Backend socket test verifies
the response. Beta also routes Task Draft creation, revision, and
promotion through a fixed Worker. The real Orchestrator socket test
verifies the Worker and fresh Kernel admission. The Worker test
executes two successive promotions and verifies the older revision.
These changes follow the paired image captures above. Repeat image
comparison before a selector change. Saved Query writes, broader
lifecycle parity, and full browser and watcher gates remain open.
