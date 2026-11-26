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
  status: draft
  version: 26
  updated_at: "2026-11-25T00:00:00+00:00"
---
## Summary

Build a transient Beta Atom snapshot

## Guarantee

Build a pinned Current Atom summary for a standalone snapshot. For a
generation, derive relations using the attested Model. On cold startup,
capture Current and Draft first. Skip archive directories during
foreground traversal. A separate Worker captures their Archived Atoms
after live admission. Seal the snapshot and Graph in the receipt.
Verify source membership and versions before admission. With verified
watcher coverage, use the watcher's completed observation in place
of a second Worker scan.

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

## Claim

### Formal Claim

The formal claim covers successful cold full generation. Compile the Model
and Structure before snapshot and Graph capture. Seal the artifacts, then
return the receipt with those seals before reporting success. Process start alone is not
success. The other guarantees remain normative prose.

```python cli
declare_cli_contract(
    interface='atom_snapshot',
    action='atom_snapshot',
    runner='managed_python',
    module='WORKERS_beta_C69.WORKERS_beta_C69__shared',
    arguments=['optional --generation-dir <empty-directory>'],
    output='succeeded',
    must_effect=(('C69.model_structure', 'compiled'), ('C69.snapshot_graph', 'captured'), ('C69.artifacts', 'sealed'), ('C69.receipt', 'returned_with_artifact_seals')),
    must_precede=((('C69.model_structure', 'compiled'), ('C69.snapshot_graph', 'captured')),
                  (('C69.snapshot_graph', 'captured'), ('C69.artifacts', 'sealed')),
                  (('C69.artifacts', 'sealed'), ('C69.receipt', 'returned_with_artifact_seals'))),
)
```


The Ticket lifecycle profile covers one admitted request with a recorded
write outcome. Capture its affected carriers against the admitted
base and check their hashes against the write receipt before
returning the outcome and delta. If projection fails, report an
explicit error without returning a successful delta.

The selected logical CLI Contract requests C16 lifecycle execution and
receives the native outcome and file effects before recording them.
Physical launch contexts and raw payloads remain open.

```python trace
declare_trace_contract(
    action='worker_ticket_lifecycle',
    output='delta_returned',
    must_effect=(
        ('C69.lifecycle_result', 'outcome_and_delta_returned'),
        ('C69.lifecycle_request', 'admitted'),
        ('C16', 'lifecycle_requested'),
        ('C16', 'outcome_and_file_effects_received'),
        ('C69.native_write_outcome', 'recorded'),
        ('C69.carrier_delta', 'captured_against_admitted_base'),
        ('C69.carrier_hashes', 'verified_against_write_receipt'),
    ),
    forbid_effect=('C69.full_generation',),
    must_precede=(
        (('C69.lifecycle_request', 'admitted'), ('C16', 'lifecycle_requested')),
        (('C16', 'lifecycle_requested'), ('C16', 'outcome_and_file_effects_received')),
        (('C16', 'outcome_and_file_effects_received'), ('C69.native_write_outcome', 'recorded')),
        (('C69.native_write_outcome', 'recorded'), ('C69.carrier_delta', 'captured_against_admitted_base')),
        (('C69.carrier_delta', 'captured_against_admitted_base'), ('C69.carrier_hashes', 'verified_against_write_receipt')),
        (('C69.carrier_hashes', 'verified_against_write_receipt'), ('C69.lifecycle_result', 'outcome_and_delta_returned')),
    ),
)
```

```python trace
declare_trace_contract(
    action='worker_ticket_lifecycle',
    output='projection_failed',
    must_effect=(
        ('C69.projection_error', 'reported'),
        ('C69.lifecycle_request', 'admitted'),
        ('C16', 'lifecycle_requested'),
        ('C16', 'outcome_and_file_effects_received'),
        ('C69.native_write_outcome', 'recorded'),
    ),
    forbid_effect=('C69.lifecycle_result', 'C69.full_generation'),
    must_precede=(
        (('C69.lifecycle_request', 'admitted'), ('C16', 'lifecycle_requested')),
        (('C16', 'lifecycle_requested'), ('C16', 'outcome_and_file_effects_received')),
        (('C16', 'outcome_and_file_effects_received'), ('C69.native_write_outcome', 'recorded')),
        (('C69.native_write_outcome', 'recorded'), ('C69.projection_error', 'reported')),
    ),
)
```

## References

AN-S-3334, AN-T-2958, and AN-T-2976.
