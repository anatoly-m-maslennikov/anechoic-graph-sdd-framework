<!-- codex-wide-delegation:start -->
## Workload-driven parallel delegation

For substantial work, identify independent investigation, implementation, and verification lanes before spawning. Give each worker a bounded deliverable, paths, exclusive edit scope, an acceptance check, and a compact return. Handle small or sequential tasks directly. Use scripts for deterministic work and reuse suitable workers.

Workers can share read-only inputs. Keep concurrent edits and shared-state mutations exclusive, and put Git index, commits, and integration under one owner.
<!-- codex-wide-delegation:end -->

<!-- codex-continuous-lanes:start -->
## Continuous lane scheduling

Policy version: `wide-delegation.1.1`.

Track lane owners, dependencies, and status alongside their briefs. Refresh the table when work finishes or dependencies change. Before waiting, dispatch all substantial ready lanes up to available capacity, ten workers, and any task-specific limit. When coordination matters, state the worker count and any blockers. Skip filler work.

Preserve release gates and verifier timeouts. Continue independent work while dependent work waits. A wait timeout leaves workers running. Stop workers only for user cancellation or a confirmed safety or scope violation.
<!-- codex-continuous-lanes:end -->
