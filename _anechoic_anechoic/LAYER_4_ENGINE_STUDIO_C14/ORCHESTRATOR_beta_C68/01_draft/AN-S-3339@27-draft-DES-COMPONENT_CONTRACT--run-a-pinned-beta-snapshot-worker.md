---
atom_family: SPEC
atom_id: AN-S-3339
container:
  component: C68
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3337
state:
  status: draft
  version: 27
  updated_at: '2026-11-25T10:37:16Z'
---
## Summary

Run a pinned Beta snapshot Worker

## Guarantee

Watch before capturing the Project. Admit Current and Draft to make
Studio ready. Load Archived Atoms in a separate Worker while the live
lane handles source changes. Report Archive progress separately.
Use the watcher's completed observation to guard startup admission.
Distinguish observed source changes from missing watcher coverage and
write one bounded stderr record with the run ID, phase, wait time, and
available Project-relative evidence for each failed fence.

Serialize live builds and admissions. Start a live build at Project
startup and after changes to watched Project sources. Watch code and dependency
inputs when the Project enables its Realization Graph. Offer the generation
to Kernel for admission. Report the active build and latest outcome. Retry a build with backoff
when its input changes during capture.
For a rebuild request matching the pinned Project, complete a fresh
generation before replying. Serialize rebuild requests with source changes.
Return the admitted generation and requested result replacements, or a
typed failure. Overlapping requests for the same target share one
admission and result map.
Treat `realization_graph` as a Graph-only request. Use the same background
Worker as the scheduled refresh and share an active Graph refresh.
Start the automatic Graph refresh after the initial Archive job settles.

Serialize each accepted lifecycle job with generation builds. Require an
admitted base. Admit the Worker’s native carrier delta against that base.
Return the recorded write outcome and projection result. Preserve known
effects on projection failure. If the Worker response is lost, report
the write outcome as unknown. Never repeat a write automatically.

Select single-Atom lifecycle facts from one admitted Kernel generation.
Use SQL for allocation, revision history, containment, and replacements.
Give the Worker the admitted Structure and needed Model rules. Run the
write in an isolated child of the warm Worker when configured. Use the
coordinated capture path for Ticket tree moves and Model input changes.
Block writes after an unconfirmed write until Kernel admits a complete
source snapshot.

Retain recent admitted carrier receipts by path. Ignore delayed watcher
events only while the file contents or absence match the recorded effect.

Retain the input proof only after Kernel accepts the generation. On a
watcher event, supply that proof to a short-lived Worker. For a
change outside the Ticket delta path, supply the Kernel Structure
when its generation matches the proof. Submit a native refresh against
that base. Use a full build if the base changed or an explicit native
rebuild was requested.

Report a failed Code Analyzer restart as a build issue and reserve the
automatic generation retry for native source currentness failures.

Attach the watcher before restart catch-up. Use Incremental Startup by
default with a compatible persisted checkpoint from Kernel. Require Worker
verification and Kernel confirmation of the base. Reuse an unchanged
projection and admit the verified Current and Draft additions, edits,
moves, and deletions before readiness.

Use a full reload when the projection database or checkpoint is missing,
or when the checkpoint is incompatible or cannot be verified. For changed
compiler inputs, request a Model and Structure compile before deciding
whether a database rebuild is required under AN-S-3389. When only Realization
Graph inputs change, request a Graph rebuild using the admitted Model and
Structure.

Admit maximum versions from the Archive filename scan for allocation.
Keep the Archive content pending until Kernel admits its background
load. Put Archive watcher events in the normal queue and process them
after that admission. A changed or vanished source skips the stale
item without failing the job. Process newer events normally. Report
elapsed time to live readiness and Archive completion separately.

Use native notifications for Ticket files where available. Retain
polling for missed changes and other inputs. Send both paths for a
Ticket rename. For supported Ticket-only changes, submit the delta
against the accepted base. Reconcile when Kernel rejects that base
or the available evidence cannot establish a safe delta.

Collect watcher events for 20 ms after the first event in a batch.
For a supported batch of up to 32 distinct Ticket paths, wait for
the warm Worker up to the measured cold load time. Use a fresh
Worker if that wait expires or the warm Worker cannot return a delta.

For 33 through 1,024 distinct Ticket paths, send the whole batch to
one fresh Worker. Use the existing broader capture when the path
set cannot be verified. Keep one admission in flight per Project.

Report the Worker mode, capture time including startup, admission
time, and delta path count for the latest successful delta.

Report the active run ID and the liveness of its cold Worker or
accepted warm child. Wait for completion or an abort for that run.
Stop its process group and report the terminal outcome as aborted.
Keep lifecycle writes and Kernel admission outside this operation.

Bind fresh Workers to the current Orchestrator process.
A Worker stops its group if that owner exits. A replacement
Orchestrator starts admission from Project state.

Record the generation trigger, output, and observed side effects as one
causal trace. Include accepted file changes and the clock-driven retry.
Send observations to the bound Kernel. Report publication errors to stderr.

## Claim

### Prose Claim

For a successful explicit rebuild through the jobs interface, the trace
records the Worker start and receipt of its sealed snapshot. It then records
the full Kernel admission request, generation commit, admission outcome, and
return of replacement IDs, in that order. Start and receipt are distinct
events. If Kernel rejects admission for the bound Project, it retains the
previous generation. Failed or aborted rebuilds return no replacement IDs.

The lifecycle projection profile covers writes with a recorded outcome and
a Worker carrier delta. It requires the selected base before the write
and reports the recorded write outcome after projection succeeds or
Kernel rejects the base or requires reconciliation.

If the Worker reply is lost after dispatch, report the write outcome as
unknown and block later writes while it is unconfirmed. A request received
while blocked is refused before Worker dispatch. Admission of a complete
source snapshot is the condition for lifting the block.

A Worker projection error received without a checked delta is reported as
a projection failure. The Orchestrator does not submit a native delta
or repeat the write on this path. C71 names the delta admission call.
This trace does not classify the exact write outcome carried with
the error.

The successful startup profile is separate from an explicit rebuild.
Attach the watcher before capture. Require completed capture and a completed
watcher observation before verified Kernel admission of Current and Draft.
Confirm live catch-up only after that admission. Capture completion and
observation completion have no required order relative to each other.
For Incremental Startup with changed Current or Draft carriers, use the
accepted checkpoint proof from Database Server C71.

This profile leaves Archive, exact Project and generation values, wire
transport, and error branches outside its scope. It does not exclude them
from startup.

### Formal Claim

```python trace
declare_trace_contract(
    interface='jobs',
    route='POST /jobs/build',
    transport='http',
    operation='generate',
    action='generate',
    output='succeeded',
    must_effect=(('C69', 'succeeded'), ('C69.artifacts', 'sealed'),
                 ('C71', 'requested'), ('C71.generation', 'committed'),
                 ('C71', 'succeeded'), ('C68.replacement_ids', 'returned')),
    must_precede=((('C69', 'succeeded'), ('C69.artifacts', 'sealed')),
                  (('C69.artifacts', 'sealed'), ('C71', 'requested')),
                  (('C71', 'requested'), ('C71.generation', 'committed')),
                  (('C71.generation', 'committed'), ('C71', 'succeeded')),
                  (('C71', 'succeeded'), ('C68.replacement_ids', 'returned'))),
)
```

```python trace
declare_trace_contract(
    interface='jobs', route='POST /jobs/build', transport='http', operation='generate',
    action='generate', output='failed', forbid_effect=('C68.replacement_ids',),
)
```

```python trace
declare_trace_contract(
    interface='jobs', route='POST /jobs/build', transport='http', operation='generate',
    action='generate', output='aborted', forbid_effect=('C71.generation', 'C68.replacement_ids'),
)
```


```python trace
declare_trace_contract(
    interface='jobs',
    route='POST /jobs/lifecycle',
    transport='http',
    operation='lifecycle',
    action='beta_lifecycle_delta_projection',
    output='projected',
    must_effect=(
        ('C68.write_outcome', 'recorded'),
        ('C71.delta', 'committed'),
        ('C68.write_outcome', 'reported'),
        ('C68.admitted_base', 'selected'),
        ('C71', 'delta_requested'),
        ('C69.lifecycle_result', 'outcome_and_delta_returned'),
    ),
    must_precede=(
        (('C68.admitted_base', 'selected'), ('C69.lifecycle_result', 'outcome_and_delta_returned')),
        (('C69.lifecycle_result', 'outcome_and_delta_returned'), ('C68.write_outcome', 'recorded')),
        (('C68.write_outcome', 'recorded'), ('C71', 'delta_requested')),
        (('C71', 'delta_requested'), ('C71.delta', 'committed')),
        (('C71.delta', 'committed'), ('C68.write_outcome', 'reported')),
    ),
)
```

```python trace
declare_trace_contract(
    interface='jobs',
    route='POST /jobs/lifecycle',
    transport='http',
    operation='lifecycle',
    action='beta_lifecycle_delta_projection',
    output='projection_rejected',
    must_effect=(
        ('C68.write_outcome', 'recorded'),
        ('C71.previous_generation', 'retained'),
        ('C68.write_outcome', 'reported'),
        ('C68.admitted_base', 'selected'),
        ('C71', 'delta_requested'),
        ('C69.lifecycle_result', 'outcome_and_delta_returned'),
    ),
    forbid_effect=('C71.delta',),
    must_precede=(
        (('C68.admitted_base', 'selected'), ('C69.lifecycle_result', 'outcome_and_delta_returned')),
        (('C69.lifecycle_result', 'outcome_and_delta_returned'), ('C68.write_outcome', 'recorded')),
        (('C68.write_outcome', 'recorded'), ('C71', 'delta_requested')),
        (('C71', 'delta_requested'), ('C71.previous_generation', 'retained')),
        (('C71.previous_generation', 'retained'), ('C68.write_outcome', 'reported')),
    ),
)
```


```python trace
declare_trace_contract(
    action='beta_lifecycle_delta_projection',
    interface='jobs',
    route='POST /jobs/lifecycle',
    transport='http',
    operation='lifecycle',
    output='write_unknown',
    must_effect=(
        ('C69.write_reply', 'missing'),
        ('C68.write_gate', 'blocked'),
        ('C68.write_outcome', 'unknown'),
        ('C69.lifecycle_dispatch', 'requested'),
    ),
    forbid_effect=('C68.automatic_write_repeat', 'C71.delta', 'C68.write_request'),
    must_precede=(
        (('C69.lifecycle_dispatch', 'requested'), ('C69.write_reply', 'missing')),
        (('C69.write_reply', 'missing'), ('C68.write_gate', 'blocked')),
        (('C68.write_gate', 'blocked'), ('C68.write_outcome', 'unknown')),
    ),
)
```

```python trace
declare_trace_contract(
    action='beta_lifecycle_delta_projection',
    interface='jobs',
    route='POST /jobs/lifecycle',
    transport='http',
    operation='lifecycle',
    output='write_blocked',
    must_effect=(
        ('C68.write_gate', 'blocked'),
        ('C68.write_request', 'rejected'),
    ),
    forbid_effect=('C69.lifecycle_dispatch', 'C71.delta'),
    must_precede=(
        (('C68.write_gate', 'blocked'), ('C68.write_request', 'rejected')),
    ),
)
```


```python trace
declare_trace_contract(
    action='beta_lifecycle_delta_projection',
    interface='jobs',
    route='POST /jobs/lifecycle',
    transport='http',
    operation='lifecycle',
    output='worker_projection_failed',
    must_effect=(
        ('C68.admitted_base', 'selected'),
        ('C69.lifecycle_dispatch', 'requested'),
        ('C69.projection_error', 'reported'),
        ('C68.worker_projection_error', 'reported'),
    ),
    forbid_effect=('C71', 'C71.delta', 'C68.automatic_write_repeat'),
    must_precede=(
        (('C68.admitted_base', 'selected'), ('C69.lifecycle_dispatch', 'requested')),
        (('C69.lifecycle_dispatch', 'requested'), ('C69.projection_error', 'reported')),
        (('C69.projection_error', 'reported'), ('C68.worker_projection_error', 'reported')),
    ),
)
```

```python trace
declare_trace_contract(
    action='beta_startup_catch_up',
    output='live_catch_up_confirmed',
    must_effect=(('C68.source_watcher', 'attached'),
                 ('C68.startup_capture', 'started'),
                 ('C68.startup_capture', 'completed'),
                 ('C68.watcher_observation', 'completed'),
                 ('startup_current_and_draft_admission', 'verified'),
                 ('current_and_draft', 'catch_up_confirmed')),
    must_precede=((('C68.source_watcher', 'attached'), ('C68.startup_capture', 'started')),
                  (('C68.startup_capture', 'started'), ('C68.startup_capture', 'completed')),
                  (('C68.source_watcher', 'attached'), ('C68.watcher_observation', 'completed')),
                  (('C68.startup_capture', 'completed'), ('startup_current_and_draft_admission', 'verified')),
                  (('C68.watcher_observation', 'completed'), ('startup_current_and_draft_admission', 'verified')),
                  (('startup_current_and_draft_admission', 'verified'), ('current_and_draft', 'catch_up_confirmed'))),
)
```

## References

AN-S-3337 and AN-T-2958.
