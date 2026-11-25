---
atom_family: SPEC
atom_id: AN-S-4738
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-24T22:51:06.533745+00:00"
relations:
  IS_REFERENCE:
  - AN-S-3346
  - AN-S-3360
---

## Summary

Measure performance and load on the production candidate

## Claim

### Prose Claim

#### Candidate

Performance and Load use an isolated instance of the exact production
candidate with production configuration and resource limits. The shared live
runtime, test and profiler dependencies, and development drivers stay outside
the candidate. Load execution uses an external development harness.

#### Performance

For a relevant change, run a short baseline and Performance check separately
from other phases against the isolated production candidate.

#### Load

For a relevant change, run a Load check separately from other phases in an
external development harness. Exclude the harness from candidate resource
measurements.

#### Soak

A long Soak is a separate opt-in check outside the ordinary short suite. It
uses the same candidate and one identified owner and process. That owner stays
alive for the full workload. It is not restarted or replaced before final
assertions.
Representative changes repeat, asynchronous work drains, and settled
CPU/memory and resource inventories are compared with the baseline.

#### Measurements and acceptance

Each run records candidate identity, workload, data, duration, concurrency,
resource limits, and cold and warm conditions. Candidate and baseline
workloads remain comparable. Record latency, throughput, errors, and resource
use and compare them with the last verified baseline and applicable limits.
Do not invent a threshold from one run or change the workload to pass.

After warm-up, record settled CPU and current memory and, where supported,
cumulative peak memory. Inspect the owner, queues, caches, result tables, and
pins used by the workload. Fail on sustained resource growth, a leaked
resource, owner loss or replacement, or an OOM event. Report a stable memory
plateau separately from allocator retention. A fall in current memory is not
growth.

Retain each executable workload's established acceptance threshold when
applicable. Aim for 0.25 s visibility of a single Ticket change as an
aspiration, distinct from the existing 1.5 s Workbench single-operation case.
Measure a 500-Atom batch separately. The archived Workbench plan
AN-S-1355@7 is historical context only. Use no numeric limit from it unless a
current runnable test declares and verifies that limit.

#### Startup timing

Each startup report identifies the container or process and its launch
clock origin. Record elapsed times on that timeline and the observed order
of each milestone.

- First carrier scan start.
- Non-Archived load start and end. End at Kernel admission of the
  queryable projection.
- Model ready, including Project Config.
- Structure ready.
- Realization Graph ready.
- Archive load end at Kernel admission.

Record public readiness and first query observations separately. Startup
replay can still gate public SQL after Kernel admission.

Record which phases rebuilt, reused prior state, or were disabled. Mark
unobserved milestones explicitly. Report foreground scan duration. When
measured, show carrier count and bytes and the nested times for census,
guarded reads and streaming, SHA-256, and checkpoint validation and
comparison. Use these details as a breakdown of scan time.

#### Lifecycle latency

For the applicable workload, retain 50 trials per operation. Report P10,
P50, P90, P95, maximum, and the sample count above 500 ms.

#### Profiling

Profiling is opt-in and separate from baseline, Performance, Load, and Soak
checks. Run it only in a development or diagnostic run. Apply AN-S-3360 to the
diagnostic image and candidate dependency inventory. Profiling output does not
satisfy an acceptance timing or resource gate.
