---
atom_family: SPEC
atom_id: AN-S-3335
container:
  component: C71
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3333
state:
  status: draft
  version: 32
  updated_at: '2026-11-25T10:46:02.868446+00:00'
---
## Summary

Serve read-only SQL for the Beta Project snapshot

## Guarantee

Admit the Model, Structure, native revisions and relations, and enabled Realization Graph
in one transaction for the bound Project. Keep the prior generation on
failed admission. Serve the accepted Model artifact bytes and canonical Structure JSON reconstructed
from accepted Structure rows and generation facts. Return the generation ID with
the Structure. Serve one read-only SQL SELECT per request, with no external access and at most 1,000 rows.
Keep a 16 MiB result budget in Kernel. Charge serialized result and
SQL bytes with a 4 KiB minimum for each result. Limit each serialized
result to 1 MiB. Refuse a new result or refresh
that would exceed capacity. Do not evict young or pinned results.
Pages keep their result across a generation update. Open Views pin results.
Unpinned results expire after the configured startup lifetime of 3,600
seconds by default. View result IDs and rows are transient.

When Workbench selects disk storage, retain the accepted generation in a
private database bound to the Project instance and Manifest digest. Offer
the compatible persisted checkpoint when that binding reopens. Commit
the input proof, carrier inventory and content hashes, and Archive
pending state with the accepted generation.

Confirm the named base before reusing the projection or accepting
Incremental Startup changes. Update affected rows and their checkpoints
together. Remove checkpoints for paths that are absent, including the
previous paths of moves. Expose the current proof to Orchestrator.
Expose DuckPGQ queries for admitted imports
and Package and Component test relationships.

Keep each Workspace bound to its Project and session. Preserve View IDs
and edits across Kernel restarts independently of query storage. Refuse
stale View revisions and keep at least one View in each Workspace.

For DuckDB Work Journal storage, admit staged records into the Project's
existing Journal table. Remove an inbox record after its commit.
Refuse conflicting bytes for an accepted record ID.

Filter, sort, and group retained inline results before paging. On an
explicit result refresh, issue replacement IDs and update any View pins
in the same locked operation. For a projection rebuild, commit the new
generation and its result refresh together. Keep the prior generation
and result IDs if capture fails.

For file Journal storage, read the admitted Project-relative Journal
directory into a connection-local `work_journal` projection before SQL.
Keep the prior rows if a carrier cannot be validated.

Record query and View Run attempts through one ordered background writer
per Project owner. Retain their seven technical fields for 48 hours in
hourly UTC files. Expose the same retained attempts through read-only
list, get, and `query_log` SQL. Check creates no attempt. A log failure
leaves the Run response intact. Drain the writer on orderly shutdown.

Return public schema fields and available distinct Status values from the
same accepted generation. Omit hints outside the supported bound.
Schema reads create no technical query attempt.

Own Saved SQL for the admitted Project. Store a successful Query or View
Run with a save request as a Bookmark. Save View snapshots one valid
read-only SELECT from a bound View or explicit SQL text without running it.
Use a canonical UUIDv7 and append under the Project Journal's fixed
`workbench-saved-items` author. Use the selected file or DuckDB storage.
Return the ID after the write. A failed save preserves a successful Run
and its query ID and returns a partial outcome.

Load saved SQL by its admitted Project ID. List bounded metadata without
SQL bodies. Read compatible historical files and accepted DuckDB records
across Journal storage changes. Saved reads do not alter their carriers.

Deliver cached results inline or as disposable files under the admitted
Project. Export the whole accepted Run or the requested Page or View
Fetch as JSON matrix, CSV, or TOON. Preserve positional values and
column names. Return a partial outcome with the existing query ID when
an export fails. Keep the result available for later reads.

Apply a Run preview cap before materializing the result. Apply a Page
or View Fetch preview only to the delivered page. Preserve the Run
preview cap when refreshing the retained result.

Publish admitted Code Access findings with the Realization Graph. Keep
declared owner bypasses visible. Omit the graph tables when disabled.

Publish `code_units` and `code_unit_calls` in the same generation.
Expose Module membership and calls through DuckPGQ. Retain the source
Module on propagated effects.

Serve structural cycles, Package coupling, and antipattern evidence
through `import_cycles`, `package_coupling`, and `antipattern_findings`.

Mark Archive pending until background reconciliation succeeds. During
Incremental Startup, prior checkpoint Archive rows may remain visible
with that marker. On cold startup, expose no Archive rows before
admission.

Admit Archive additions, edits, moves, and deletions with their relations
and carrier hashes against the latest live generation in one transaction.
Preserve Current and Draft rows and the Realization Graph. Clear the
pending marker only when Archive admission succeeds.

Accept a native-only refresh against the named current generation.
Validate the native snapshot against the admitted Model. Replace Atom
and native relation rows in one transaction. Retain Model, Structure,
and Realization Graph rows when the request contains only a native
snapshot. When the request also supplies a Realization Graph and its
digest, validate it against the admitted Structure and replace it
in the same transaction. Retain the exact Model and Structure.
Refuse a stale generation and retain the prior state on failure.

A native carrier delta names the current generation and up to 1,024 affected paths.
Publish the changed Atom rows and Model-defined relations together in one
transaction, including their graph rows and Current Lens membership.
Retain the accepted Model, Structure, and Realization Graph. Request
reconciliation when the delta cannot preserve relation ownership.

Derive Component flows from observed events. Expose their causal
links and shared-action candidates in SQL. Admit each bound trace atomically. Preserve the
event stream across generation rebuilds and disk reopen.

## Claim

### Prose Claim

The query route models one new SQL Run. Paging and other Database Server
operations have separate inputs and outcomes.

The artifact read profile covers Model and Structure. A successful read
matches the Project binding and returns accepted content with its corresponding
generation ID. A foreign instance or missing generation returns no pair.

The full generation admission profile covers the bound Project. A commit
pairs the artifacts and Project snapshot, including the enabled Realization
Graph where relevant, in one transaction. A validation or admission failure
retains the prior generation. A foreign instance cannot commit a generation.
Exact payload and database atomicity verification remain deferred.

The carrier delta profile checks the Project binding and named base
before admission. One commit publishes the changed Atom and Model-defined
relation rows with their graph rows and Current Lens membership. The
accepted Model, Structure, and Realization Graph stay in place. A stale
base or a delta that cannot preserve relation ownership leaves the
previous projection in place.

### Formal Claim

```python trace
declare_trace_contract(
    action='beta_database_query',
    interface='database_api',
    route='query',
    transport='http',
    operation='POST /database',
    output='succeeded',
    must_effect=(('C71', 'generation_checked'), ('C71', 'read_only_select_admitted'), ('C71', 'query_retained')),
    forbid_effect=('sql_mutation', 'sql_external_access'),
    must_precede=((('C71', 'generation_checked'), ('C71', 'query_retained')),
                  (('C71', 'read_only_select_admitted'), ('C71', 'query_retained'))),
)
```

```python trace
declare_trace_contract(
    action='beta_database_artifact_read',
    output='succeeded',
    must_effect=(('project_binding', 'matched'), ('artifact_content_generation', 'paired')),
    must_precede=((('project_binding', 'matched'), ('artifact_content_generation', 'paired')),),
)
```

```python trace
declare_trace_contract(
    action='beta_database_artifact_read',
    output='foreign_instance',
    forbid_effect=('artifact_content_generation',),
)
```

```python trace
declare_trace_contract(
    action='beta_database_artifact_read',
    output='no_generation',
    forbid_effect=('artifact_content_generation',),
)
```


```python trace
declare_trace_contract(
    action='beta_full_generation_admission',
    interface='database_api',
    route='admit',
    transport='http',
    operation='PUT /generation',
    output='succeeded',
    must_effect=(('C71.project_binding', 'matched'), ('C71.admission_inputs', 'verified'),
                 ('C71.generation', 'committed')),
    must_precede=((('C71.project_binding', 'matched'), ('C71.admission_inputs', 'verified')),
                  (('C71.admission_inputs', 'verified'), ('C71.generation', 'committed'))),
)
```

```python trace
declare_trace_contract(
    action='beta_full_generation_admission',
    interface='database_api',
    route='admit',
    transport='http',
    operation='PUT /generation',
    output='failed',
    must_effect=(('C71.project_binding', 'matched'), ('C71.previous_generation', 'retained')),
    forbid_effect=('C71.generation',),
    must_precede=((('C71.project_binding', 'matched'), ('C71.previous_generation', 'retained')),),
)
```

```python trace
declare_trace_contract(
    action='beta_full_generation_admission',
    interface='database_api',
    route='admit',
    transport='http',
    operation='PUT /generation',
    output='foreign_instance',
    forbid_effect=('C71.generation',),
)
```


```python trace
declare_trace_contract(
    interface='database_api',
    route='admit_native_delta',
    transport='http',
    operation='PUT /generation/native-delta',
    action='beta_native_delta_admission',
    output='admitted',
    must_effect=(
        ('C71.base_generation', 'matched'),
        ('C71.delta', 'committed'),
        ('C71.model_structure_realization_graph', 'retained'),
        ('C71.project_binding', 'matched'),
        ('C71.relation_ownership', 'preserved'),
    ),
    must_precede=(
        (('C71.project_binding', 'matched'), ('C71.base_generation', 'matched')),
        (('C71.base_generation', 'matched'), ('C71.relation_ownership', 'preserved')),
        (('C71.relation_ownership', 'preserved'), ('C71.delta', 'committed')),
        (('C71.delta', 'committed'), ('C71.model_structure_realization_graph', 'retained')),
    ),
)
```

```python trace
declare_trace_contract(
    interface='database_api',
    route='admit_native_delta',
    transport='http',
    operation='PUT /generation/native-delta',
    action='beta_native_delta_admission',
    output='stale_base',
    must_effect=(
        ('C71.base_generation', 'stale'),
        ('C71.previous_generation', 'retained'),
        ('C71.project_binding', 'matched'),
    ),
    forbid_effect=('C71.delta',),
    must_precede=(
        (('C71.project_binding', 'matched'), ('C71.base_generation', 'stale')),
        (('C71.base_generation', 'stale'), ('C71.previous_generation', 'retained')),
    ),
)
```

```python trace
declare_trace_contract(
    interface='database_api',
    route='admit_native_delta',
    transport='http',
    operation='PUT /generation/native-delta',
    action='beta_native_delta_admission',
    output='reconciliation_required',
    must_effect=(
        ('C71.reconciliation', 'required'),
        ('C71.previous_generation', 'retained'),
        ('C71.project_binding', 'matched'),
        ('C71.base_generation', 'matched'),
    ),
    forbid_effect=('C71.delta',),
    must_precede=(
        (('C71.project_binding', 'matched'), ('C71.base_generation', 'matched')),
        (('C71.base_generation', 'matched'), ('C71.reconciliation', 'required')),
        (('C71.reconciliation', 'required'), ('C71.previous_generation', 'retained')),
    ),
)
```

```python trace
declare_trace_contract(
    interface='database_api',
    route='admit_native_delta',
    transport='http',
    operation='PUT /generation/native-delta',
    action='beta_native_delta_admission',
    output='foreign_instance',
    forbid_effect=('C71.delta',),
)
```

## Source alignment to resolve

The existing guarantee describes Structure JSON reconstructed from accepted
rows. AN-S-4797@1 describes accepted Model or Structure bytes, and
AN-S-4798@1 describes a Host read under a lock. Resolve these accounts and
the read sequence before activation. This profile does not select a Structure
representation or prescribe a lock.
