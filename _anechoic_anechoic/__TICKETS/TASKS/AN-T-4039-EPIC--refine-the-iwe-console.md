---
atom_family: TKT
atom_id: AN-T-4039
container:
  component: C43
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T22:21:13Z"
---
## Summary

IWE Console Refinement

## Objective

Make IWE Console a place to query the Project, browse its Atoms and
Structure, inspect imports, and run supported lifecycle and rebuild
operations.

## Scope

Use SQL as the source for regular Console tabs. Add Table, Document,
Graph, Imports, and Structure views. Use one full Document view for
the modal, tabs, and the right pane. Keep runtime health and rebuild
controls in the separate Diagnostics tab.

## Workflow

1. Review and update the Structure of the Components and Component
   Seeds that serve IWE Console. Assign an owner to each capability.
2. Create or update their Manifests and formal boundaries. Declare
   imports and exports, server and client interfaces and calls, and
   state reads and writes. Define the public Contract guarantees.
3. Create formal Solutions that show how each Component meets its
   Contract. Link each Solution to its Contract and describe any
   delegation through the declared interfaces.
4. Review each affected Component's other Specs. Fix inconsistencies,
   retire obsolete Specs, and add missing behavior and QA Specs.
   Check Lens whitelists and compile the formal Specs.
5. Implement the six Tasks below and verify them against the reviewed
   Specs.

## Frontend Lenses

Use SWD for development rules and QA for verification. Use DES for
design and DES/IO for human-facing interface behavior. Check these
against the current Frontend Manifest whitelist. The Manifest also
allows DevOps for delivery. See AN-S-3060 and AN-S-5007.

## Structure decision

C43 owns the Console contract. C46 owns the browser views and edit state.
C21 forwards Console operations to C91. C91 routes query and workspace
operations to C71, and document, lifecycle, and rebuild operations to C68.
C68 coordinates C69 Workers. C61 supplies the Realization Graph analysis.
C93 supplies Component and Seed Structure. These are existing owners.
C16 supplies the same Ticket transition policy for Document choices and
lifecycle writes.

## Implementation

1. AN-T-4040 · Add the Console SQL builder and View directives
2. AN-T-4041 · Open Atom documents in the modal, tab, and pane
3. AN-T-4042 · Edit, create, and change Atom status in the Console
4. AN-T-4043 · Show Atom relations and import violations in graphs
5. AN-T-4044 · Show Project Structure and its Specs
6. AN-T-4045 · Add Console Diagnostics and rebuild actions

## Done when

Verify the Task acceptance checks through the supported Console entry
points. Cover query building, document navigation, Draft autosave and
promotion, relation and import graphs, Structure links, and rebuild
feedback. Require a green test suite and zero import violations.
Cover all six Tasks with formal Specs, compare the implementation against
those Specs, and require a review with no open findings. Generate and run
tests from the formal Specs.

Start Local Release after AN-T-3476 and AN-T-4046 are Done.

## Verification

The built Console passed 61 browser checks, including cases generated
from the C46 Contract and Solution for Draft reuse, autosave, creation,
and promotion. Chrome opened exact Atom revisions from grouped results,
full cell values, Document headers, and Structure purposes.
Project interface tests verified exact Atom reads, authored Draft
updates, persisted View SQL, and rebuilds. A full rebuild loads new
source. A Graph rebuild preserves the Atom index, Model, and Structure.

Chrome verified both rebuild actions against a disposable Studio runtime.
The generated refusal cases verified that Diagnostics refreshes Worker
state and ingestion issues when a rebuild fails.

The real shared HTTP stack passed exact Document reads, Draft creation,
editing, and promotion. The same test verified that a second Project
kept its own revision. The Structure test uses the public compiler CLI.
The Document tests cover configured Current Ticket Status choices and
reject choices from a stale generation.
Document relation tests verified stable and exact links on Current and
exact links on Draft and Archived revisions. Draft removal controls use
the selected Header's authored relations, so generated containment
edges remain read-only. The generated browser case verified this boundary.

Four proposed Manifests supply missing Component purposes. The Structure
query selects exact Active Tier 0 Solutions that answer the admitted
Manifest revision. The projection query excluded stale pins and
ineligible Solutions. Seven browser checks passed, including exact
Manifest and Solution links and the Seed's embedded Solution.

Chrome ran the formal Ticket edit case against a disposable Studio. It
created a Ticket through the UI, reopened the exact Draft, autosaved an
edit, and verified the promoted Current body. A refused Summary edit
kept the unsaved text, showed the error, and sent no promotion request.

C21's Contract and Solution AN-S-5044 matched the HTTP route and all three
outcomes in Lean. The generated cases passed against the shared runtime.
They verify Current and exact reads and refusal of a mismatched Project name.

The Console Graph queries ran against the real Kernel. Bare and exact
Current references resolved the same relations and Spec Bindings while
keeping their document links. The Archived revision had no Current edges.
The generated exact-reference browser case opened the selected revision.
The Imports Graph marked denied and undeclared occurrences without marking
an allowed occurrence between the same modules.
The generated browser case verified horizontal Imports with a red
violation edge. Kernel Check, Run, and Save accepted that directive and
preserved the authored SQL and comments.

The Save Contract matched three observed SQL round trips in Lean. They
covered plain SELECT, a quoted View keyword, and Unicode with line endings
and comments. The Console and Kernel recognize View directives with comments
and keep SQL strings and nested expressions separate from the directive.
Chrome verified the real Studio path from a commented View query to its
Document and reopened the authored SQL from the saved View link. Both
standalone migration cases passed against the same disposable runtime.
The generated Document and Graph cases verified the error for multiple
Atom reference columns. Lean matched both outcomes.

The full suite and zero-import gate remain open. The Realization Graph
reported 154 violations against the Active Manifests and 132 with the
nine proposed Manifests. Lifecycle capture and persisted Structure
backfill tests cleared three violations by exercising the owning entry
points. All 16 focused tests passed. The proposed Manifests still clear
the nine findings in the Atom Document and lifecycle context modules.
The proposed C16 Manifest clears exact Draft dispatch through its owning
Package. The proposed C16 and C30 Manifests admit the shared parent lookup
for Spec revision. The revision, standalone Contract refusal, and file
effect tests passed.
Static passed bytecode and Python import checks. The Project Spec
creation path and its tests now meet 45/300. All seven route tests
passed. Static still stops on 29 size violations in the checkout.

MCP tests use the owning shared entries. The proposed C21 Manifest
clears the remaining 11 findings in MCP Patchbay. All 26 focused host
tests passed, and both image test modules loaded.

Lean matched the 23 tested translations and the C43 to C46 call. The
exact Draft Contract and Solution matched all four declared outcomes.
Generated CLI tests confirmed that a refused replacement leaves the
Draft unchanged and a failed readback reports an unknown modify receipt.
The formal review still has open State, I/O, Code Access, and symbolic SQL
equality obligations. The revised Console Specs are Drafts.

The Console now reruns Builder edits, refuses stale Run revisions and
result pages, and keeps the active Draft editor open during tab rename.
The generated cases verified those behaviors and the exact returned Draft
reference. The native allocator returned revision 2 after version 1 and
revision 5 when Archive already held version 4.

Shared HTTP and MCP bind each call to its admitted Project instance.
API refuses a changed selection before dispatch. MCP refuses a success
receipt for a different or missing Project. The real two-Project test
passed with identical Project names. Local Lean translated the revised
Contracts and Solutions. Static comparison of symbolic bindings remains
unresolved. The generated browser cases check concrete observations.

## Current verification checkpoint

The Realization Graph for committed revision `1e2588dd54e3d` reports
44 denied imports and one undeclared bypass across the Project.
The IWE Console tree has zero violations. The Project has 39
uncertain occurrences. Static remains red.

C46 Active AN-S-3060@17 and AN-S-3372@10 generate 66 browser cases.
The 63 earlier case records stayed identical. Their Console suite
passed across the main run and the focused Diagnostics rerun.
The shared HTTP test also passed Project isolation, lifecycle writes,
and the three C21 Draft document forwarding cases.

Lean directly matched seven new C46 actions. Builder Run, lifecycle,
and Draft editing still have unresolved event bindings. State, I/O,
and Code Access comparison remains unresolved across Components.
The Draft guard specifies three outcomes for navigation during a pending
save. All 13 focused lifecycle browser cases passed. Lean matched all 17
field comparisons captured for the three new outcomes.

The Graph overlay joins Current Component and Package bindings by
exact revision. Current Kernel accepts trailing View directives on
Check and Run and preserves authored SQL on Save.

Current Structure SQL returns exact Component and Seed documents.
The DuckDB owner test verified watcher refresh with Imports disabled
and retained-database reuse. All seven Structure browser cases passed.
Graph-only rebuild preserves Atom and Structure facts. The Project
rebuild refreshes them from source.
The C59 Contract and Solution match in Lean for success and disabled
refusal. Both generated cases passed against the Current Kernel.

Current Diagnostics reads indexed Atom and issue counts from Kernel
and Worker Runs through its existing route. The bound API checks and
all eight Diagnostics browser cases passed. The two-Project HTTP test
verified detailed status and Project isolation with the test compiler
deadline disabled. The 15-second compiler deadline prevented readiness
in the default run. All six focused Manifest and OpenAPI checks passed
with the test compiler deadline disabled. AN-T-3476 still gates Local
Release.
