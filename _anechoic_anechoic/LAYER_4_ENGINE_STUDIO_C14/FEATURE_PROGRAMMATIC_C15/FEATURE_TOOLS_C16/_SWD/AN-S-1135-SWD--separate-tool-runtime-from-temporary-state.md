---
atom_family: SPEC
atom_id: AN-S-1135
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 33
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Separate Tool runtime from temporary state


# Separate Tool runtime from temporary state

place ANECHOIC-owned persistent operational state under the current Project's
`.anechoic_runtime/` root. place selected Tool releases **and** stable launchers
under `.anechoic_runtime/tools/`; keep these carriers reconstructible from
governed source **and** configuration. give **every** Tool-owned log, session, database,
service-state, **and** resumable-state Carrier an owned runtime descendant. these
Carriers **may** preserve a non-reconstructible operational timeline.

Apply AN-S-1245 and AN-S-1258 to temporary Carriers.

keep both trees non-authoritative. deleting `.anechoic_tmp/` can lose **only**
disposable state. deleting `.anechoic_runtime/` **may** require reinstallation **or**
lose operational history **and** resumable progress, but cannot lose a governed
Artifact **or** Project Journal history. Preserve accepted Journal records in configured external sinks during cleanup or reinstallation.
