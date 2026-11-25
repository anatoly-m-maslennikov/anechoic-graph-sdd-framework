---
atom_family: SPEC
atom_id: AN-S-3340
container:
  component: C70
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3338
state:
  status: draft
  version: 28
  updated_at: "2026-11-25T10:58:29.166498+00:00"
---
## Summary

Admit Projects and serve Beta Workbench queries

## Guarantee

Admit an active Project Manifest and bind API requests to that Project.
Expose the read-only SQL run, page, check, and schema Tools. Return
typed inline pages from the Project's Kernel. Check SQL without
retaining a result. Expose admitted Realization Graph tables through the
SQL schema and the accepted generation's optional Status values.
Send Worker status requests to Orchestrator. Expose the active run ID
and Worker liveness. Forward an abort for an exact run only to its
Project's Orchestrator. On a shared host, status and abort can reach
the first build while SQL waits for admission. These controls do not
start a Project.

On a shared host, admit only Projects within the configured root and
enforce each Project's Tool blacklist. Reuse its Kernel and Orchestrator
within the configured capacity. Evict the least recently used idle
Project to admit another when capacity is full.

Pass the Project's Workbench storage choice or the host default to its
Kernel. Wait for verified Current and Draft admission before advertising
the Project as ready. Return a startup failure when live admission fails.
Serve queries while archive loading continues. Expose incomplete history
in health and the Archive Worker outcome in Workbench status.

Expose Workspace open, list, and get and View create, duplicate, list,
get, update, focus, rename, and remove. Send changes to the owning Kernel.
Resolve the session and Project from the API request and host binding.
Forward View run, check, and inline fetch to Kernel. Pass Workbench
result lifetime, Journal storage, and the file Journal path from the
admitted settings. Forward grid operations to Kernel. For a projection
rebuild, request generation with its refresh target through
Orchestrator. Return the replacement IDs that Kernel committed. Expose
Project-scoped query history tools and the Kernel `query_log` SQL view.
Keep their request and response fields the same through Workbench and MCP.

Submit Task or Epic Draft creation, revision, exact Draft promotion,
Current Ticket status changes, native Ticket archive, and Ticket Asset
creation and direct updates to Orchestrator. Return the lifecycle outcome
after the carrier delta is admitted or projection fails.
Report projection failure with known file effects and distinguish an
unknown write outcome from a rejected request.

Expose Saved SQL load, list, and View Save for the admitted Project.
Forward a Run save request and standalone View Save to its Kernel. Use
the admitted Project binding for the write. Validate the Project and
origin of a load URL before forwarding its ID. Use the request origin
for links. For stdio, use the admitted configured Workbench page.

Return the retained result and query ID if a successful Run cannot save.
Include the Kernel's partial outcome and save error.

Forward preview and delivery options to Kernel. Default to file delivery
for HTTP Query Run, Query Page, and View Fetch. Default to automatic
delivery for MCP Query Run. Honor explicit inline delivery. Preserve
the bound file descriptor, query ID, and any partial export outcome.

In the packaged shared host, request a Project lease from the private
peer owner. Keep the Project's Kernel and Orchestrator across Backend
and MCP restarts. Release the lease when the request ends or its
connection closes. The peer owner enforces capacity and owns the warm
Worker. In packaged single-Project HTTP mode, pin one Project for the
container. The peer owner starts Kernel and Orchestrator and confirms
initial admission. The API validates that binding before listening.
Keep the peers across independent API and MCP restarts.

If Kernel or Orchestrator exits, replace the bound pair and re-admit
the pinned Project. In the shared host, recovery starts when the
failed Project's leases end. Other Projects and the transport
processes continue. In the single-Project HTTP runtime, suspend the
API and MCP until the replacement pair completes admission.
Keep the last accepted disk generation available for catch-up.
Any result or run held only in a stopped process can be lost.

For standalone or stdio, the runtime owns its local peers and warm Worker
for the lifetime of its caller's connection.

Measure warm Worker readiness and send the elapsed time to
Orchestrator. Use a fresh Worker when the warm Worker cannot start.


## Claim

### Prose Claim

For an admitted Project, a successful projection rebuild returns the
replacement IDs after requesting generation through Orchestrator. This
claim covers the Orchestrator path for an `all` or projection table target.

A successful shared Backend Tool call binds the Project, validates the
Tool against its enabled definitions, dispatches it, and returns a raw
Tool result. A refused or failed call returns a failure. This claim does
not compare arguments, context, or result values.

For a shared Ticket Tool call, distinguish an unknown write outcome, a
known write with a projection failure, and a request refused while the
Orchestrator has blocked writes. Preserve the Orchestrator outcome.

### Formal Claim

```python trace
declare_trace_contract(
    action='beta_backend_rebuild_projection',
    output='succeeded',
    must_effect=(('C68', 'requested'), ('C68.replacement_ids', 'returned')),
    must_precede=((('C68', 'requested'), ('C68.replacement_ids', 'returned')),),
)
```

```python trace
declare_trace_contract(
    action='beta_backend_tool_call',
    interface='shared_workbench_api',
    route='POST /tools',
    transport='http',
    operation='tool_call',
    output='succeeded',
    must_effect=(('C70.project_binding', 'admitted'),
                 ('C70.tool_validation', 'validated'),
                 ('C70.tool_dispatch', 'dispatched'),
                 ('C70.raw_tool_result', 'returned')),
    must_precede=((('C70.project_binding', 'admitted'), ('C70.tool_validation', 'validated')),
                  (('C70.tool_validation', 'validated'), ('C70.tool_dispatch', 'dispatched')),
                  (('C70.tool_dispatch', 'dispatched'), ('C70.raw_tool_result', 'returned'))),
)
```


```python trace
declare_trace_contract(
    action='beta_backend_lifecycle_failures',
    interface='shared_workbench_api',
    route='POST /tools',
    transport='http',
    operation='tool_call',
    output='write_unknown',
    must_effect=(
        ('C70.write_outcome', 'unknown'),
        ('C70.project_binding', 'admitted'),
        ('C70.tool_validation', 'validated'),
        ('C68', 'lifecycle_requested'),
        ('C68.write_outcome', 'unknown'),
    ),
    forbid_effect=('C70.write_request', 'C70.projection'),
    must_precede=(
        (('C70.project_binding', 'admitted'), ('C70.tool_validation', 'validated')),
        (('C70.tool_validation', 'validated'), ('C68', 'lifecycle_requested')),
        (('C68', 'lifecycle_requested'), ('C68.write_outcome', 'unknown')),
        (('C68.write_outcome', 'unknown'), ('C70.write_outcome', 'unknown')),
    ),
)
```

```python trace
declare_trace_contract(
    action='beta_backend_lifecycle_failures',
    interface='shared_workbench_api',
    route='POST /tools',
    transport='http',
    operation='tool_call',
    output='projection_rejected',
    must_effect=(
        ('C70.write_outcome', 'known'),
        ('C70.projection', 'failed'),
        ('C70.project_binding', 'admitted'),
        ('C70.tool_validation', 'validated'),
        ('C68', 'lifecycle_requested'),
        ('C68.write_outcome', 'reported'),
    ),
    forbid_effect=('C70.write_request',),
    must_precede=(
        (('C70.project_binding', 'admitted'), ('C70.tool_validation', 'validated')),
        (('C70.tool_validation', 'validated'), ('C68', 'lifecycle_requested')),
        (('C68', 'lifecycle_requested'), ('C68.write_outcome', 'reported')),
        (('C68.write_outcome', 'reported'), ('C70.write_outcome', 'known')),
        (('C70.write_outcome', 'known'), ('C70.projection', 'failed')),
    ),
)
```

```python trace
declare_trace_contract(
    action='beta_backend_lifecycle_failures',
    interface='shared_workbench_api',
    route='POST /tools',
    transport='http',
    operation='tool_call',
    output='write_blocked',
    must_effect=(
        ('C70.write_request', 'rejected'),
        ('C70.project_binding', 'admitted'),
        ('C70.tool_validation', 'validated'),
        ('C68', 'lifecycle_requested'),
        ('C68.write_request', 'rejected'),
    ),
    forbid_effect=('C70.write_outcome', 'C70.projection'),
    must_precede=(
        (('C70.project_binding', 'admitted'), ('C70.tool_validation', 'validated')),
        (('C70.tool_validation', 'validated'), ('C68', 'lifecycle_requested')),
        (('C68', 'lifecycle_requested'), ('C68.write_request', 'rejected')),
        (('C68.write_request', 'rejected'), ('C70.write_request', 'rejected')),
    ),
)
```
