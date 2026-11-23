---
atom_family: SPEC
atom_id: AN-S-3363
container:
  component: C68
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3339@20
  IS_REFERENCE:
  - AN-S-3361@2
state:
  status: active
  version: 2
  updated_at: '2026-11-22T23:33:05.345105+00:00'
---

## Summary

Model the Orchestrator rebuild flow

## Claim

### Prose Claim

An accepted explicit rebuild clears the retained input proof and starts a
cold Worker. A successful Worker result proceeds to full Kernel admission.
Record whether successful admission requires a reuse proof write. If it
does, store the proof before reporting the admitted generation. Otherwise
report success directly. Report a failure or accepted Worker abort at the
corresponding exit.

The Formal Claim covers the observed boundary events for a rebuild with
one trigger. It defines the allowed order and outcomes of those events.

### Formal Claim

```python
component_workflow(
    component="C68",
    action="generate",
    machine={
        "id": "orchestrator_rebuild",
        "initial": "idle",
        "states": {
            "idle": {"on": {
                "rebuild_request": {"target": "clear_proof", "guard": {
                    "type": "matchesTrace", "params": {"kind": "trigger"}}},
            }},
            "clear_proof": {"on": {
                "generation_reuse_write": {"target": "start_worker", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C68.generation_reuse",
                        "outcome": "succeeded", "detail": {"state": "cleared"}}}},
            }},
            "start_worker": {"on": {
                "worker_started": [
                    {"target": "await_worker", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C69", "outcome": "succeeded"}}},
                    {"target": "report_failure", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C69", "outcome": "failed"}}},
                ],
            }},
            "await_worker": {"on": {
                "generation_admission": [
                    {"target": "store_proof", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C71", "outcome": "succeeded",
                            "detail": {"reuse_proof_present": True}}}},
                    {"target": "report_success", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C71", "outcome": "succeeded",
                            "detail": {"reuse_proof_present": False}}}},
                    {"target": "report_failure", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "effect", "target": "C71", "outcome": "failed"}}},
                ],
                "generation_result": [
                    {"target": "failed", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "failed",
                            "detail": {"code": "generation_failed"}}}},
                    {"target": "aborted", "guard": {
                        "type": "matchesTrace", "params": {
                            "kind": "output", "outcome": "aborted",
                            "detail": {"code": "worker_aborted"}}}},
                ],
            }},
            "store_proof": {"on": {
                "generation_reuse_write": {"target": "report_success", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "effect", "target": "C68.generation_reuse",
                        "outcome": "succeeded", "detail": {"state": "stored"}}}},
            }},
            "report_success": {"on": {
                "generation_result": {"target": "succeeded", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "output", "outcome": "succeeded", "detail": {"kind": "full"}}}},
            }},
            "report_failure": {"on": {
                "generation_result": {"target": "failed", "guard": {
                    "type": "matchesTrace", "params": {
                        "kind": "output", "outcome": "failed",
                        "detail": {"code": "generation_failed"}}}},
            }},
            "succeeded": {"type": "final"},
            "failed": {"type": "final"},
            "aborted": {"type": "final"},
        },
    },
)
```

## Details

Install the locked Node dependencies with `npm ci` in the Engine Studio
Import Graph's `WORKFLOW_SPEC` directory. Use the Engine Python environment
and set `PYTHONPATH=LAYER_4_ENGINE_STUDIO_C14`. Keep `node` and `lean` on
the executable path.

Run `python -m IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.workflow_spec`
with this Atom path and `render` to write Mermaid. Use `check <matrix.json>`
to check a run. Export one run from `flow_events` as a Workbench JSON matrix
with all columns and order the rows by `sequence`.

The check reports `matched`, `different`, or `unresolved`. A run needs a
recorded rebuild trigger, a terminal output, and a complete event sequence.
Use the archived revision for traces recorded before admission included
`reuse_proof_present`.
