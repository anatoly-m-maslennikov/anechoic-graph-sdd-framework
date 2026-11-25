---
atom_family: SPEC
atom_id: AN-S-3336
container:
  component: C69
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3334
state:
  status: active
  version: 25
  updated_at: "2026-11-23T10:26:33.104737+00:00"
---
## Summary

Build a transient Beta Atom snapshot

## Guarantee

Build a pinned Current Atom summary for a standalone snapshot. For a
generation, derive relations using the attested Model. On cold startup,
capture Current and Draft first. Skip archive directories during
foreground traversal. A separate Worker captures their Archived Atoms
after live admission. Seal the snapshot and Graph in the receipt.

Use the watcher's completed observation to guard admission of the
startup base for covered inputs. Orchestrator replays observed changes
against that base.

Verify source membership and versions for external or unwatched inputs.
If coverage is lost, verify the affected inputs before admission.
Use a broader capture if their scope is unknown.

For other captures, verify source membership and versions before
admission. With verified watcher coverage, use its completed
observation in place of a second Worker scan.

Derive named Python, JavaScript, and TypeScript Code Units from captured
Modules. Resolve calls to known Functions and Methods using captured
imports and source bindings. Include declaration and call locations. Use
those call sites to check reached effects in Lean.

Reuse captured sources and import sites for bounded antipattern review.
Keep findings with unresolved owners or execution order visible.

Run one admitted Ticket operation per lifecycle invocation. Create a Task
or Epic Draft, revise a Current Task or Epic into a Draft, promote
an exact Draft, change a Current Ticket's status, archive an exact native
Ticket revision, create a Ticket Asset, or update its Markdown body.
Apply the admitted lifecycle definition and
its Ticket tree effects. Require a different Current Atom to declare
the replacement before archive. Refuse Ticket containers. Bind the operation
to the pinned Project. For a single-Atom write, use the admitted SQL
facts, Structure, and Model rules. Read exact pinned sources through
the Adapter. Compile again for coordinated Ticket tree moves and Model input changes.
Capture the affected native carriers against the admitted base and check
their hashes against the write receipt. Return the native outcome and delta,
or an explicit projection error. Do not build a full generation for the write.

For ordinary source changes, revalidate the input signatures of the
accepted Model, Structure, and Graph before and after native capture.
Return the new native snapshot and its base generation when all
inputs match. If only Graph inputs changed and Kernel supplies the
Structure for that base, rebuild the Realization Graph. Return it
with the native snapshot, digests, and updated input proof. Preserve
the accepted Model and Structure. Use a full build if the required
proof is unavailable or changes during capture.

If the Code Analyzer confirms that graph inputs changed during capture,
restart only the analyzer once with the same Model, Structure, and native
capture, and return a build issue if graph inputs change again.

For Incremental Startup, use the compatible persisted checkpoint to
compare the deterministic folder and carrier path inventory and SHA-256
content hashes. Reuse unchanged data. Capture only additions, edits, and
move destinations. Include the previous path of a move and each missing
path as removals in the change set.

Verify Current and Draft changes before live admission. Verify Archive
changes in the background. Require a full reload if the checkpoint
cannot be verified or a Model, Structure, or compiler schema input
changed. When only Realization Graph inputs changed, rebuild the Graph
with the admitted Model and Structure.

For a supported Ticket-only change, capture up to 1,024 named paths
in one fresh Worker. Return their native delta against the accepted base. An
absent file identifies a removal. Use the existing refresh path when
the file scope, Project Manifest, or source cannot be verified.

A managed fresh Worker stops its isolated process group
when its bound Orchestrator exits. Validate the parent binding before
processing the request.

The warm Worker loads its code once. It accepts one Ticket capture
of up to 32 paths before the caller's start deadline. Report the new
child's PID on acceptance. The child runs without a time limit. On
client write-half close, stop and reap its process group. Return no
delta if capture fails or stops. The warm parent can accept another
capture and retains no Project data. Preload the C16 writer in the same
broker. Run a single-Atom write and its exact delta capture in one child.

## References

AN-S-3334, AN-T-2958, and AN-T-2976.
