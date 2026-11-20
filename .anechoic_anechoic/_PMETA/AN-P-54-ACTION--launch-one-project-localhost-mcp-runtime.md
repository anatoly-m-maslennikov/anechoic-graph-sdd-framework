---
identity:
  atom_id: AN-P-54
context:
  container:
    component: C21
  tier: 1
  template: action
state:
  status: active
  version: 14
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

launch one Project localhost MCP runtime

## Operation

launch Project localhost MCP runtime means the reusable bounded Action that selects one Project context and returns a directly reachable localhost MCP endpoint only after exact image admission and loopback Host/Origin-protected host-side readiness. Its boundary is one Project MCP service, not a Release action, proxy, worker controller, queue controller, or Workflow executor.

### Applicable when

An Operator invokes project-mcp for one Project-local HTTP MCP service with declared --project-root or a safe explicit root, optional direct --control-root, explicit readable --source-root for image/build closure, optional --no-build, optional --port equality assertion, and bounded readiness timeout. No password, bearer, Authorization value, or credential source is accepted. build_if_missing is true unless --no-build; the selected root need not be a Git root.

### Action

1. Resolve exactly one ProjectSelection by CA-R-1900; return its attributable refusal unchanged for missing, unsafe, invalid, ambiguous, or changed bindings. Read its required Project Settings `[project_mcp] http_port` integer in `1..65535`; stop before Docker effects if missing or invalid, or if a supplied `--port` differs.
2. Acquire only that identity's lock, calculate the admitted source fingerprint from --source-root, and resolve one immutable matching image by CA-R-1901. Missing source input is IMAGE_INPUT_UNAVAILABLE with a safe --source-root request; runtime N and Release/package boundaries remain unchanged. Build only when build_if_missing=true; --no-build refuses. Refuse wrong/mutable images rather than retagging or replacing.
3. Reuse only one healthy matching selected-Project service after the bounded loopback Host/Origin readiness probe. A live unhealthy/mismatched service refuses without stop, restart, recreate, replacement, or fallback.
4. If absent, start only direct mcp-http with `127.0.0.1:<http_port>:8092`. Docker binds the configured port atomically; read back exactly one mapping and require it to match Project Settings, including on reuse. An occupied port fails without another port or service replacement. Do not pre-reserve a port or start proxy, worker, queue, Agent, Workflow, Tool, or Release actions.
5. Perform the bounded Host/Origin-protected host-side MCP initialization/readiness exchange over the returned loopback URL. Container health, PID, or open socket alone is insufficient; return URL/ready only after success.

### Outcome and stop

Return JSON with exactly one safe disposition (started, reused, refused, failed, or busy) and one of READY_STARTED, READY_REUSED, PROJECT_SELECTION_REFUSED, IMAGE_INPUT_UNAVAILABLE, IMAGE_REFUSED, PROJECT_LOCK_BUSY, RUNTIME_MISMATCH, RUNTIME_UNHEALTHY, BUILD_FAILED, DOCKER_START_FAILED, DOCKER_PUBLICATION_FAILED, or READINESS_FAILED. Include safe Project identity, immutable image digest/fingerprint, service and readiness facts; on ready success only return http://127.0.0.1:<http_port>/anechoic/mcp, and --output url emits only that URL. Never return credentials or claim success before Host/Origin readiness. Stop on selection, image, lock, Docker-publication, or readiness failure; do not infer success, substitute Project/image/port, retry unknown effects, or widen into queue/worker/Workflow/proxy/Release.
