---
atom_family: SPEC
atom_id: AN-S-2554
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 42
  updated_at: 2026-10-24 20:48:49 +0400
---
## Summary

Deliver project-local commit automation

# Deliver project-local commit automation

deliver four peer Tool units, COMMIT_TRIGGER, COMMIT_CONTEXT, APPEND_CHANGE_RECORDS, **and** COMMIT_CHANGE_SET, plus one independently supervised repository-local COMMIT_AUTOMATION service. canonical source **and** shared libraries live under `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS`; INSTALL_TOOLS publishes a content-addressed self-contained release under `.anechoic_runtime/tools`; persistent operational state stays below `.anechoic_runtime`; **and** disposable staging, cache, **and** atomic-write intermediates stay below `.anechoic_tmp`.

the Codex transport is one asynchronous PostToolUse command Hook. it normalizes one host event, atomically renames one immutable envelope into .anechoic_runtime/state/commit_automation/inbox/, **and** exits. it **contains** no broad scan, graph traversal, before-event snapshot, context gathering, Journal append, Git mutation, retry, **or** pipeline-worker spawn. the background service consumes the durable inbox, performs low-frequency repository reconciliation, asks one pure manager for the admissible graph **or** next command, persists **every** transition, **and** lets a mechanical Scheduler dispatch COMMIT_CONTEXT followed by independent real-change **and** Journal branches. APPEND_CHANGE_RECORDS appends provenance independently; COMMIT_CHANGE_SET creates real-change commits **and** later Journal-only batch commits through one fenced gate.

the service preserves accepted work across Hook completion, manager termination, pause, stop, start, reload, crash, **and** release replacement. it enforces one active commit-creating gate item per repository; later commit items remain pending while context gathering **and** eligible Journal preparation continue independently. workers are atomic **and** non-deciding. COMMIT_CHANGE_SET owns **only** the sealed commit boundary **and** never imports **or** orchestrates its peers. real-change commits **and** Journal-only commits remain separate gate items.

the release provides install, status, enable, disable, pause, resume, narrow, stop, start, reload, uninstall, recovery, **and** reconciliation controls. Status reports the active autonomy envelope **and** Work binding, adapters, process **and** selected release, queue **and** action phases, gate **and** lease state, budget **and** circuit state, pending **or** blocked work, dead letters, last completed real-change **and** Journal batch, **and** deterministic recovery instructions. budget exhaustion, envelope expiry **or** narrowing, **and** integrity-sensitive failures pause autonomous execution for Operator recovery. Hooks **and** adapters are transport **only**; Git Hooks remain narrow synchronous Evaluations **or** observers. the release performs no branch, upstream, remote, synchronization, push, tag, **or** release operation.

the executable realization uses the envelope-check Action CA-O-037 under CA-R-1385.
