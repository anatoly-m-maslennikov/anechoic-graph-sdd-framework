---
atom_family: SPEC
atom_id: AN-S-1551
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

verify Project MCP launch results and readiness

## Claim

### Prose Claim

the Evaluation **must** verify that every launcher disposition is structured, safe, and attributable, and that a success URL is returned only after actual loopback Host/Origin-protected host readiness.

## Details

### Result and readiness checks

- Exercise every exact CA-O-235 safe code: READY_STARTED, READY_REUSED, PROJECT_SELECTION_REFUSED, IMAGE_INPUT_UNAVAILABLE, IMAGE_REFUSED, PROJECT_LOCK_BUSY, RUNTIME_MISMATCH, RUNTIME_UNHEALTHY, BUILD_FAILED, DOCKER_START_FAILED, DOCKER_PUBLICATION_FAILED, and READINESS_FAILED. Each maps to one disposition; only ready started/reused includes a URL. Verify default JSON and --output url, with no URL for non-success.
- In the real-Docker gate, connect to the Docker-reported 127.0.0.1 port and complete Host/Origin-protected MCP initialization/readiness. Container health/open socket alone cannot produce a success URL; Authorization neither grants nor denies localhost readiness.
- Assert output contains only safe Project identity/root references, immutable digest/fingerprint, service/publication/readiness facts, and bounded diagnostics. Search structured output/ordinary diagnostics for password, bearer, Authorization, credential URL query/fragment, and secret environment values; none may occur.
- Verify readiness and failures start no worker, queue, Agent, Workflow, Tool call, proxy, or Release action. Failed/refused outcomes preserve a live selected runtime and claim no replacement/completion.
