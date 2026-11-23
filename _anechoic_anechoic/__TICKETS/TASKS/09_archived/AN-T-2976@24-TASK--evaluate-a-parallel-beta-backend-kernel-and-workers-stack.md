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
  version: 24
  updated_at: "2026-11-22T19:17:49.906680+00:00"
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
  direct code. Import symbols from the owning Package's shared entry
  under Code Access. Record exact owner bypasses in the Realization
  Graph so repeated bypasses inform structural moves under AN-T-2986.
  Give each Seed one Manifest, an ID such as `CS123`, and
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

## Saved SQL write actor

Beta reads historical saved items under the selected Project across
Journal storage changes. It can load those items without execution.

AN-S-170 requires the already sealed operator GitHub username,
configured timestamp timezone, and local date. Its appender uses
100-event segments and returns a replayable digest receipt. The
historical writer described in AN-S-2547 uses a service label and
1,000-row segments. Keep that data available through the read path.
Apply AN-S-170 to new appends.

Which trusted provider binds the requesting operator to a GitHub
username in local stdio, Web, and shared MCP? The current ingress
provides a Project binding and session ID. Those identify the
request scope. They supply no verified operator identity. Define
the provider and private propagation before enabling Saved SQL
writes. For a successful query where saving is refused, retain
the result and return a partial outcome with a save error.

## Watcher, browser, and result delivery

The next paired images were
`sha256:1474d641915e956163a360eff958a16447a3b3ab787a598ca0eec3a90fa1eca5`
(Current) and
`sha256:036c11fee91addbfe8e751ef570567183b68766edb51dcf9783ef3cf7a4d18c2`
(Beta). Both came from one frozen engine source and passed the Local
Release canary.

Current passed the three focused Docker cases. Beta passed Task promotion
with immediate query visibility and the populated-directory watcher case.
Beta's native Atom create was still absent at the existing 1.5-second
deadline. Orchestrator had started the Worker by the failed observation.

Current passed the browser suite. Beta passed 21 cases, failed five,
and had seven unrun at the 115-second suite deadline. Three failures
involved saved references. Two cases did not render a result grid.
Keep the saved-write identity requirement and the existing deadlines.

The checkout now delivers bounded inline and file results through the
owning Kernel. Query Run preview caps capture. Query Page and View Fetch
preview cap delivery. Socket tests verified JSON, CSV, TOON, retained
query IDs, and delivery defaults. The checked-out lifecycle lane also
supports Epic creation and Current Ticket status changes. The actual
Worker verified rejection of an invalid status and a stale definition.

The checked-out Realization Graph found zero denied or unresolved
cross-Component imports. Its Beta check passed all 12 implementation
and Test Packages. The broader package work continues under AN-T-2946
and AN-T-2986.

## Native Atom watcher deadline

The paired Docker fixture now allows at most 30 seconds per native Atom
mutation. It still checks exact query-visible rows and Graph relations
for create, edit, rename, and delete. It records elapsed time separately
for each mutation. This is the paired fixture check. AN-S-1370 defines
the separate controlled 5,000-Atom resource benchmark.

On one CPU per candidate, Current `sha256:51ca7c1aa4e1942846110a8ff6518460d10e0811df02e37a7106f551356080d9` passed with
0.785 s create, 0.919 s edit,
0.923 s rename, and 1.051 s delete.

Beta `sha256:fe5f7845b21e2f6b39a562657339d4e7cae638f1c36bca2765f9d40693c99469` passed with 11.542 s create,
16.708 s edit, 19.592 s rename, and
16.347 s delete. Both images passed the release canary.

A separate one-CPU profile of an earlier Beta image measured 7.39 s for
the full Worker build and 0.15 s for Kernel admission. The profile
measures one build. The watcher measurements are elapsed file-change
to query visibility.

## Watcher verification at 20 seconds

The paired Docker fixture enforces 20 seconds per native Atom change.
It checks the exact Atom and relation rows and records time from the
file mutation to SQL visibility.

The earlier Beta image `sha256:fe5f7845b21e2f6b39a562657339d4e7cae638f1c36bca2765f9d40693c99469` passed with 16.633 s create, 7.330 s edit, 6.011 s rename, and 5.381 s delete.

The new Current image `sha256:64669fb59ef6b18368ecdeb9f86acd2f64dd7b391d6b03049c376537da687fc7` passed with 0.365 s create, 1.020 s edit, 0.997 s rename, and 0.974 s delete.

The new Beta image `sha256:4de53e962696c19f21f6db12abb095911183cc227eccad90587971c3fd13c040` passed with 5.718 s create, 6.153 s edit, 6.262 s rename, and 5.930 s delete.

The Worker builds the Graph before its final expanded native capture.
It uses that capture for both the native projection and the final
source check. This removes one full capture per generation. A
changed-and-restored Ticket blocked publication in the focused check.

## Native Ticket archive comparison

Both candidates passed the same MCP archive test against separate
disposable Projects with the active Model. They refused archive
without a replacement. After a different Current Ticket declared
`IS_REPLACEMENT_FOR`, both archived the exact revision and returned the
expected SQL projection immediately after the request.

Current `sha256:64669fb59ef6b18368ecdeb9f86acd2f64dd7b391d6b03049c376537da687fc7`
completed the entire test in 91.464 seconds. Beta
`sha256:4de53e962696c19f21f6db12abb095911183cc227eccad90587971c3fd13c040`
completed it in 274.769 seconds. These times include
fixture startup and several lifecycle operations.

The earlier bare fixture omitted the relation declaration. Its Beta
projection correctly refused the undeclared relation. The archive
fixture now admits a Project with the declaration before any writes.

## Watcher latency profile

On Beta `sha256:4de53e962696c19f21f6db12abb095911183cc227eccad90587971c3fd13c040`, the settled one-CPU Docker fixture
detected each change and started its only generation in 0.116 to
0.164 seconds. Generation and admission took 11.284 to 18.319
seconds. The exact SQL result appeared 11.472 to 18.511 seconds after
the file change. The four operations all met the 20-second limit.

A separate generation profile on the same image measured 2.743 seconds
for Model and Structure compilation, 3.214 seconds for the Realization
Graph, and 1.172 seconds for both native captures. Worker total was
7.131 seconds. Kernel admission took 0.153 seconds. This measures
the stages in one separate run, so it does not explain the slower
operations on its own.

Optimize repeated generation work for file changes. Preserve the fresh
input and atomic admission checks. The watcher event delay is a small
part of the observed time.

## Native-only watcher refresh

Orchestrator retains the input proof of the last accepted generation.
A short-lived Worker checks that Model, Structure, and Graph inputs
match before and after native capture. On a match, Kernel accepts a
native-only update against the current generation in one transaction.
If input proof is unavailable, the Worker builds the full generation.

The exact Beta image `sha256:347b8bb622ad5f380aa12058fea8b4f1383f5450a7dda2c517ba82b4094f9268` used native-only admission for
all four ordinary Ticket operations in the settled Docker fixture:
create 4.408 s, edit 4.078 s, rename 4.536 s, delete 8.349 s. After a code edit, Orchestrator reported a full build
and the new unresolved import appeared in SQL.

The earlier profile on the same fixture ran full builds for the four
Ticket changes and took 11.472 to 18.511 seconds to SQL visibility.
These are separate samples. The 20-second correctness check still
requires the exact Atom and relation rows for each operation.

## Bounded Ticket refresh

For supported Ticket changes, Orchestrator collects the affected paths.
The Worker captures those paths against the accepted Model. Kernel
patches the addressed Atom and relation rows in one transaction. The
watcher uses native events where possible and keeps polling active.
A rename sends the old and new paths together.

Twenty host Ticket mutations reached SQL as bounded deltas in Beta
`sha256:3a63ca61a35a64e63aead56b47748f403f3a24c4dce108087db5e896ede11e7b`. Median visibility was 1.732 seconds.
The separate code-change probe expired at 20 seconds while its full
generation was active.

In the instrumented Docker image `sha256:122b5a6b92b5b05ca889dcf317eac8c46bc05ea54cd770b231aec22101a2c106`, the same container
alternated Worker cache modes. The visible samples included 9
uncached Workers and 7 precompiled Workers. The medians were 2680 and 787 ms for
the Worker, 149 and 101 ms for Kernel
admission, and 3158 and 1075 ms from host write
to SQL. The two modes met 250 ms on 0 and 0
mutations, respectively.

The next candidate is one warm Worker per installation for bounded
Ticket changes, with isolated jobs. Larger batches and changes to
generation inputs can use a separate batch Worker. Keep admission
serial within each Project. A local warm forkserver probe used fresh
children and produced the same delta in a median 24.5 ms per child.
Docker visibility under 250 ms remains an open acceptance check.

## Warm Worker measurements

The Ticket delta loader accepts up to 32 distinct changed paths in one
job. A larger batch uses the native snapshot path if the accepted
artifacts still apply. Otherwise the Worker builds a new generation.

In the Docker forkserver experiment, 16 Ticket changes reached SQL
through the delta path. The Worker median was 432 ms. The median
from host write to SQL was 792 ms, with zero samples within 250 ms.

The single-threaded broker experiment forked a fresh child per job.
Docker create and edit reached SQL in 468 and 313 ms. The Worker
round trips were 89 and 27 ms. A rename used the native snapshot
path and took 14.039 seconds. The following delete produced no
visible update or new job within 20 seconds.

Use one preloaded Worker per runtime for ordinary Ticket batches.
Start a separate Worker for larger batches when its startup and
execution costs justify it. Keep one admission in flight per Project.
The warm Docker experiments have yet to satisfy the latency and
correctness checks for the full mutation sequence.
