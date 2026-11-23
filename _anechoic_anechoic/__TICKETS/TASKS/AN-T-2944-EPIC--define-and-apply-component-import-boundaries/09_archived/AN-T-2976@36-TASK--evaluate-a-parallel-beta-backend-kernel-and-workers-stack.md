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
  version: 36
  updated_at: "2026-11-23T01:33:34.333462+00:00"
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

## Saved SQL write decision

Saved SQL uses the fixed Project Journal author
`workbench-saved-items` from AN-S-2547. The Operator dropped the
verified GitHub operator requirement for these writes. Preserve the
plain append behavior, canonical UUIDv7 IDs, and compatibility reads
from both Journal modes and historical saved files.

Use the existing Project binding at each ingress. Backend forwards
the save operation to Kernel. Kernel returns the new ID after
storage accepts the snapshot. If a successful run cannot save,
return the query result and a partial outcome with a save error.

The sealed-append requirements in AN-S-170 apply to their existing
scope. This decision selects the plain Saved SQL behavior from
AN-S-2547, AN-S-1661, and AN-S-451.

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
That run applied the former Saved SQL guard and the existing deadlines.

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

## Smart Worker startup

Beta collects events for 20 ms after the first event in each batch.
The Backend starts one warm Worker per runtime and shares it across
admitted Projects. Each warm job captures its Ticket delta in a fresh
child. The warm parent retains the loaded code.

The wait budget for a bounded Ticket batch equals the measured time
from warm Worker spawn to readiness. Use that measurement to estimate
fresh Worker load time. Use a fresh Worker if the warm slot misses the
deadline, capture cannot return a delta, or the batch needs a broader
capture. Kernel admits one result at a time for each Project.

Docker watcher and two-Project MCP checks passed on the paired images.

- Current `sha256:31040bde26c99345d705d87df3e69381429537857b0a92bd2ee040efecd8368a`
- Beta `sha256:23eac3a4a102e999ef716fe34182af76c15beee0ff0e4bfb88f989d5dffa8290`

Both Beta Orchestrators used the same warm Worker socket. A cold Worker
built the first generation. All 12 measured host mutations used
warm deltas. Median SQL visibility was 120 ms, with
9 of 12 samples within 250 ms. The slowest took
421 ms, so the fixture does not show a 250 ms upper bound.

## Bulk Ticket delta

Orchestrator sends a batch of 33 through 1,024 distinct Ticket paths
to one fresh Worker. The Worker captures those paths against the
accepted generation. Kernel applies their Atom rows and Model-defined
relations in one transaction. The existing warm path covers up to
32 paths. Unsupported changes use the existing broader capture.

In the Docker fixture, all 500 edited Atoms reached SQL with their
expected graph relations. Visibility took 13.50
seconds in the baseline and 6.07 seconds after this change.
The later run admitted a 13-path warm delta and cold deltas of 380
and 107 paths. The two cold admissions took 0.29 and
0.24 seconds. Their Worker times were 2.67 and
2.41 seconds.

Bulk benchmark image `sha256:51a2ce690eea4ea64be1d32dc06451a5c4fea5ddad0340018ecdc5d4d9a76c37`.

## Cutover checks

The Beta restart case ended before the restart. The save request
returned a query result without a saved-query ID. The admitted
operator identity in the Saved SQL section is still required.

The full-site canary exited during Backend startup when a two-second
Kernel health request timed out. Docker reported exit code 3 and
no OOM kill. The Backend now retries health timeouts within the
existing startup deadline. The full-site canary still failed. The Backend reached its
startup deadline without an admitted initial generation.

## Single-capture candidate comparison

Workers reuse the parsed native carrier capture after Model, Structure,
and Graph build. They recheck carrier membership and file versions
before publishing a generation. The focused test rejects a changed
carrier even when it is restored to its earlier bytes. A separate
check rejects a new carrier after capture.

Built Current `sha256:59829998e340d1a9c3b304bc1b2e2e8c2435737888d2d129c92dbee76bf4a925` and Beta
`sha256:6cad7d654af519525f7acc746c1c3c50627164a7f03e7598b669fd8e9f2b3325` from the same frozen source. Both one-CPU packaged
canaries initialized MCP and returned the Framework SQL result. Current
took 60.61 seconds and Beta took 72.17 seconds from the readiness probe.
Beta also passed with the full Atom tree and an empty source package
in 47.75 seconds.

- Current ran 14 image tests with 1 failures and 0 errors.
- Beta ran 14 image tests with 5 failures and 1 errors.
- Beta still stops before the restart when the query has no saved ID.
- Native Atom watcher observations were create 0.172 s, edit 0.173 s, rename 0.174 s, delete 0.162 s.
- A sampled full graph update spent 10.57 s in the Worker and 0.22 s in admission. The code watcher gate is 10 s.
- Current browser rerun outside the launcher sandbox passed.
- Beta browser rerun outside the launcher sandbox failed.
- Beta Playwright ran with Chrome. It passed 22 scenarios, failed 5,
  and left 6 unrun at its time limit. Failures covered saved View
  identity and result-grid visibility. The cause of the two grid
  failures is still unverified.
- Required host suite passed 518 tests across 85 Modules.

## Disk catch-up and precompiled imports

Kernel records the accepted native carrier paths and content hashes in
its database. At startup Worker checks both path sets. A deleted path
appears only in the checkpoint. A rename has one removed and one
added path. Readiness waits for catch-up.

The disk-backed Docker check kept the same database. An edit with
restored mtime, a deletion, and a rename used one four-path Ticket
delta and reached readiness in 4.57 s. Next, unchanged input reused the
same accepted generation in 4.13 s. A separate offline Python import
appeared after a graph refresh in 4.93 s. These times used the small
image-test Project. Both packaged canaries with the full Atom tree
passed on the same candidate pair.

Precompiled imports are specified in AN-S-3360. The candidate images
loaded their packaged caches with bytecode writes disabled. Profiler
code stays in diagnostic test images. Use the existing Engine,
Release, and Setup dependency locks. Engine has dev, test, and prod roles.

Installed Studio source without tests or generated output occupies
2685.88 KB in Current and 2362.05 KB in Beta. Source unique to either stack
occupies 688.29 KB in Current and 364.46 KB in Beta.

In the Beta image, five of six focused graph and watcher cases passed.
The new-directory storm missed its first graph observation deadline.
Saved SQL writes still require the trusted operator binding.

## Run controls and single-container deployment

Orchestrator exposes live cold-Worker status and abort by exact run ID.
An abort stops the Worker process group while it is collecting inputs.
Kernel admission and lifecycle writes remain outside this operation.
Backend exposes status and forwards abort to the bound Orchestrator.
The host integration check passed five cases, including real process abort.
Warm Ticket Workers retain their existing dispatch and completion bounds.

Diagnostic watcher and readiness observations can run without a latency
cutoff. The timed repeat passed all six watcher cases on the immutable
precompiled Beta candidate. The earlier directory-storm miss remains
an observed timing discrepancy on the same image.

The full packaged Beta restart reused the accepted generation and
served the MCP query in 62.01 s after Docker restart returned.
The cold readiness sample for that run was 139.20 s.
Runtime Setup keeps one container and its existing OOM behavior.
AN-T-2958 records independent process lifetime as a deployment target.

The 536 required host tests and the 300/45 source checks passed.
The Backend test completed SQL while the cold Worker was alive,
then aborted that exact run. The MCP process exposed both Tools.
The deadline-free Docker observation passed the directory-storm
and native Ticket watcher cases.

## Shared runtime recovery

The packaged shared Beta runtime keeps one container and its existing
memory limit and OOM handling. Its Runtime supervisor runs the Project
peer owner separately from Backend and MCP. Release or disconnect ends
a request lease. A transport restart keeps the admitted Project and its
warm Worker.

The shared candidate test killed Backend and MCP separately. Both
Projects kept their Kernel and Orchestrator PIDs and served their
original in-memory query IDs after each restart. Direct single-Project
launches still own their local peers.

Shared Project status and abort can reach the first build before SQL
admission. Orchestrator tracks and aborts the exact cold process or
accepted warm capture. Abort stops and reaps that group. The warm
Worker accepts the next capture. Kernel admission and lifecycle writes
retain their separate boundaries.

The full-site Current and Beta canaries passed on `sha256:e7911b282778ae4d49553581f2e6a5be5f7d5da8f52347985553c05310513617` and
`sha256:63a03a725a7b15a68475ba6d3e9d95dce3ed7966ebc478a5c90ff71ecc28bd9d`. A prior Beta sample exited at the
Kernel's 15-second peer handshake cutoff, without an OOM kill. The
passing Beta monitors peer liveness and cancellation during startup.

The current Realization Graph found 12 Beta implementation and Test
Packages with exactly one shared entry and zero forbidden imports. The
whole Project still has non-shared inbound imports. The Workbench
browser tests now select bundled Chromium. Discovery found 33 cases.
A complete browser run and the saved SQL actor binding remain open.

## Automatic recovery of all four services

The packaged single-Project and shared Beta modes restart Backend and
MCP independently. If Kernel or Orchestrator exits, re-admit its Project
with a replacement pair. Single-Project HTTP restarts the transport
processes after admission. In shared mode, other Projects and transports
stay active. Keep the deployment in one container with its existing OOM
policy.

The single-Project image test killed each of the four services in turn.
Backend and MCP replacement kept the original query page. Core
replacement admitted the same Project and served a fresh query. The
shared image test observed background core replacement before the
next query. The other Project retained its peer PIDs and original page.

The packaged tests passed on Current `sha256:1d330c8a834c24a3650c6c6828e3798373871dc67acca5f607ad06a3e713214d`
and Beta `sha256:89e89b438dcf0218aa11b27c01aaf8e1faef65f2d39a57b4b706def203e81778`.
The required host run passed 544 cases. The additional shared recovery
case passed separately. The 300/45 checks passed on the tested
snapshot. A later Workflow compiler edit exceeded the function limit.

The full-site Current and Beta canaries passed on the same pair.
The final Beta shared recovery test passed on `sha256:b8e8c5f5141906123c33fee9311ccd4b96e7f9b052c9adfd4f9773afa3109b12`.
Shared recovery waits for admission while the replacement peers live.
It has no fixed elapsed-time cutoff. Recovery tests stopped idle peers.

The Realization Graph found 12 compliant Beta implementation and Test
Packages and zero forbidden Beta imports. Project-wide non-shared
inbound sites fell from 1,191 to 1,078. The Project-wide migration
remains open. The pinned previous-image selector still uses its mounted
codec and passed against the retained ready image.

## Managed Worker cleanup

If Orchestrator exits, its active cold Snapshot Worker or lifecycle
Worker stops its isolated process group. Project recovery starts a
fresh admission. The failure ends the interrupted run.

The two Worker entry tests killed the launching parent while stdin
remained open. The Worker and its same-group child stopped in both
cases. A warm capture stops when its client socket closes.

The paired Current image was
`sha256:bd9e729474158479b21b0240315254649b583c5d4e4fe57e0b60931470926566`.
The Beta image was
`sha256:f46b44b2fd8023de8c33d3c76abe8db2f3b8caecc3162f6141325929d2050413`.
Both passed the packaged single-Project and shared-Project checks
and the full-site release canary.
Beta recovered after each of the four services was killed. The tests
verified query continuity across Backend and MCP restarts and fresh
admission after Kernel or Orchestrator restart.

The required host suite passed 548 tests. The static suite passed,
including the 300-line Module and 45-line function limits. The live
source Realization Graph found 12 compliant Beta Packages and zero
forbidden Beta imports. The Project-wide off-entry count fell from
1,078 to 901. The applicable component contracts and bindings record
the Worker lifetime rule.


## Linux Workbench browser verification

The packaged Beta browser run verified 13 test files against the
build inputs and used bundled Playwright Chromium. It passed 30 of
34 cases. Editor replacement, standalone autosave, cross-context
sync, and formatter errors passed. The paging case confirmed that
a refused save keeps its error visible while results remain usable.

Four Saved SQL cases failed against the former operator guard and
missing standalone Save View path. A prior run used stale test
files. The verified run supersedes that result.

## Package entry verification

Route imports through the owning entries for Atom Lifecycle, Claim
Adapters, Formal Model Generator, and Current Kernel projection.
The entry exports preserve symbol identity. The Component Manifests
record the corresponding Code Access rules.

The Realization Graph found 108 Atom Lifecycle off-entry imports
before the change and zero after it. The Project-wide count fell
from 901 to 721. Beta still has 12 compliant implementation
and Test Packages and zero forbidden imports. Project-wide Package
access cleanup remains open.

Current `sha256:bcc0348fdb83ff4be97ef73eb40e06fd5d83fa05df3327eff5ee1af5aa619824` and
Beta `sha256:80f342a3befb080d2fe2c7aff23bc0195e315c097a44a42445ad003b733051ed`
passed single-Project HTTP, shared Project, and full-site release
canary checks. Their common build inputs matched except the selector.
The 300/45 checks and all 548 required host tests passed.

The prior candidate lacked Saved SQL writes. Restore Run & Save
and standalone Save View according to the current decision above.

## Package migration and cutover scope

The source graph found one shared entry in all 88 authored Packages.
Imports that bypass entries fell from 721 to 479. The graph still
reports zero unresolved imports and zero forbidden Beta or
cross-Component imports. AN-T-2946 records the authored scope.

Current `sha256:92fbc9e1637e3dc3bd5ea7d5cc7553c7ad4a9eb99b4a85dfa7ff92527c441a3c` and
Beta `sha256:6a247ae6263121f3771a0267abaf5b16ff9c1cf71657fe0f5921af40c4624c8b`
passed the single-Project HTTP and shared Project checks, the
Realization Graph and external import inventory cases, and the
full-site release canaries. All 548 required host tests passed.
The 300/45 checks passed. This pair predates the Saved SQL and MCP
changes for cutover.

For cutover, finish Saved SQL, the focused MCP bridge rewrite, and
the Adapters entry migration. Verify the resulting Current and Beta
images. Promote the verified Beta stack and then pause the broader
Package migration. Reassess remaining Current Kernel and Backend
imports after cutover.
