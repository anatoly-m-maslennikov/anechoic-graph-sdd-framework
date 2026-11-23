---
atom_family: SPEC
atom_id: AN-S-1135
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 22
  updated_at: 2026-10-24 00:51:05 +0400
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

allocate a Tool-owned **and**, **when** concurrency is possible, run-specific
descendant below `.anechoic_tmp/` for **every** temporary, scratch, staging,
cache, Python bytecode cache, build, intermediate Evaluation, atomic-write intermediate, **and**
interrupted-cleanup Carrier. pass that descendant explicitly **to** temporary-file
APIs **and** configure **every** invoked dependency **to** use it. do **not** use the
repository root, process working directory, source tree, Project control root,
Runtime State root, **or** host temporary location as a fallback.

for atomic replacement, stage below `.anechoic_tmp/` **and** verify the
required same-filesystem atomicity precondition **before** mutation. stop with a
stable boundary diagnostic **when** safe placement cannot be established. attempt
bounded cleanup, but keep **every** cleanup remnant confined **to** temporary state.

keep both trees non-authoritative. deleting `.anechoic_tmp/` can lose **only**
disposable state. deleting `.anechoic_runtime/` **may** require reinstallation **or**
lose operational history **and** resumable progress, but cannot lose a governed
Artifact **or** Project Journal history.
