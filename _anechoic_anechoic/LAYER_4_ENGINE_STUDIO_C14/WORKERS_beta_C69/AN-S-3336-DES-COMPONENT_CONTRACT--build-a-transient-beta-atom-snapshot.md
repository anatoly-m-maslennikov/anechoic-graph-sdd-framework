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
  status: "active"
  version: 22
  updated_at: "2026-11-22T23:25:08.356588+00:00"
---
## Summary

Build a transient Beta Atom snapshot

## Guarantee

Build a pinned Current Atom summary for a standalone snapshot. For a
generation, capture Current, Draft, and Archived revisions and derive
relations using the attested Model. Build the Model, Structure, and
enabled Realization Graph from the same unchanged source capture. Seal
the snapshot and Graph in the receipt. Capture native carriers once.
Reject changes to their membership or file versions before publishing.

Derive named Python, JavaScript, and TypeScript Code Units from captured
Modules. Resolve calls to known Functions and Methods using captured
imports and source bindings. Include declaration and call locations. Use
those call sites to check reached effects in Lean.

Reuse captured sources and import sites for bounded antipattern review.
Keep findings with unresolved owners or execution order visible.

Run one admitted Ticket operation per lifecycle invocation. Create a Task
or Epic Draft, revise a Current Task or Epic into a Draft, promote
an exact Draft, change a Current Ticket's status, or archive an exact
native Ticket revision, or directly update the Markdown body of a Ticket Asset.
Apply the admitted lifecycle definition and
its Ticket tree effects. Require a different Current Atom to declare
the replacement before archive. Refuse Ticket containers. Bind the operation
to the pinned Project and fresh Model and Structure.
Return the native outcome and known file effects.

For ordinary source changes, revalidate the input signatures of the
accepted Model, Structure, and Graph before and after native capture.
Return the new native snapshot and its base generation when all
inputs match. If only Graph inputs changed and Kernel supplies the
Structure for that base, rebuild the Realization Graph. Return it
with the native snapshot, digests, and updated input proof. Preserve
the accepted Model and Structure. Use a full build if the required
proof is unavailable or changes during capture.

On restart, compare admitted and current carrier paths and SHA-256
hashes. A missing path is a deletion. Reuse an unchanged generation.
When only eligible Ticket paths changed, capture those paths.
Reconcile broader changes with the applicable native, Graph, or
full generation path.

For a supported Ticket-only change, capture up to 1,024 named paths
in one fresh Worker. Return their native delta against the accepted base. An
absent file identifies a removal. Use the existing refresh path when
the file scope, Project Manifest, or source cannot be verified.

A managed cold or lifecycle Worker stops its isolated process group
when its bound Orchestrator exits. Validate the parent binding before
processing the request.

The warm Worker loads its code once. It accepts one Ticket capture
of up to 32 paths before the caller's start deadline. Report the new
child's PID on acceptance. The child runs without a time limit. On
client write-half close, stop and reap its process group. Return no
delta if capture fails or stops. The warm parent can accept another
capture and retains no Project data.

## References

AN-S-3334, AN-T-2958, and AN-T-2976.
