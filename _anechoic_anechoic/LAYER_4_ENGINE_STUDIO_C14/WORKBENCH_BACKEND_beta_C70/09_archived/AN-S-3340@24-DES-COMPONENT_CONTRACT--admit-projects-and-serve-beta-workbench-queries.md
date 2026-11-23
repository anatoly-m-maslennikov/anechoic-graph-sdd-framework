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
  status: "archived"
  version: 24
  updated_at: "2026-11-23T00:32:58.888819+00:00"
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
Kernel. Wait for startup verification and any offline changes to be
admitted before advertising the Project as ready. Return a startup
failure if Kernel and Orchestrator cannot complete catch-up.

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
Current Ticket status changes, native Ticket archive, and Ticket Asset direct
updates to Orchestrator.
Return the lifecycle outcome after generation admission.
Report projection failure with known file effects and distinguish an
unknown write outcome from a rejected request.

Expose Saved SQL load and list for the admitted Project. Validate the
Project and origin of a load URL before forwarding its ID. Include links
when the public Workbench address is available.

When a successful query or View Run requests a save and the actor is
unavailable, return the retained result with a partial outcome and a
save error. Saved SQL writes require a trusted, sealed operator identity.

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

## References

AN-S-3338 and AN-T-2958.
