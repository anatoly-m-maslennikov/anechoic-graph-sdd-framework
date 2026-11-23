---
atom_family: SPEC
atom_id: AN-S-3339
container:
  component: C68
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 17
  updated_at: "2026-11-22T22:17:21.880924+00:00"
---
## Summary

Run a pinned Beta snapshot Worker

## Guarantee

Run one pinned build at a time. Start a build at Project startup and
after changes to watched Project sources. Watch code and dependency
inputs when the Project enables its Realization Graph. Offer the generation
to Kernel for admission. Report the active build and latest outcome. Retry a build with backoff
when its input changes during capture.
For a rebuild request matching the pinned Project, complete a fresh
generation before replying. Serialize rebuild requests with source changes.
Return the admitted generation and requested result replacements, or a
typed failure. Overlapping requests for the same target share one
admission and result map.

Serialize each accepted Task, Epic, or Ticket Asset lifecycle job with generation builds. After
the Worker returns, offer a fresh generation for admission. Reply with
the recorded write outcome and the projection result. Preserve known
effects when admission fails. If the Worker response is lost, report
the write outcome as unknown. Never repeat a write automatically.

Retain the input proof only after Kernel accepts the generation. On a
watcher event, supply that proof to a short-lived Worker. For a
change outside the Ticket delta path, supply the Kernel Structure
when its generation matches the proof. Submit a native or native
and Realization Graph refresh against that base. Run a full build
if the base changed. Explicit rebuilds and lifecycle refreshes use
the full build path.

Attach the watcher before restart catch-up. Use an admitted proof
and carrier checkpoint supplied by Kernel when available. Reuse the
same generation only after Worker verifies its inputs and Kernel
confirms the base. Admit a targeted delta when the offline changes
fit that path.

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

Report the active run ID and cold Worker liveness. Wait for a cold
Worker to exit or accept an abort for its exact active run. Terminate
that process group and report the terminal outcome as aborted. Keep
lifecycle writes and Kernel admission outside this abort operation.

Record the generation trigger, output, and observed side effects as one
causal trace. Include accepted file changes and the clock-driven retry.
Send observations to the bound Kernel. Report publication errors to stderr.

## References

AN-S-3337 and AN-T-2958.
