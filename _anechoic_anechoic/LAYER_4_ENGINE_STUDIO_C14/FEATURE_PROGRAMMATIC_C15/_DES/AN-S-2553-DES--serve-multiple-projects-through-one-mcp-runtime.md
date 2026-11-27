---
atom_family: SPEC
atom_id: AN-S-2553
container:
  component: C15
tier: 4
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---

## Summary

Serve multiple Projects through one MCP runtime

## Claim

### Prose Claim

The shared runtime **must** serve each operation under exactly one validated Project binding. It **must not** conflate Project identity, source or Tool frontier, mutable state, or effects. The supported Codex path is session → Project-local `ca` Skill → every Tool call carrying outer `project_root` and the unchanged native request → the same MCP.

## Details

### Runtime and installation

Deliver one Docker container and one external HTTP MCP endpoint. Read host configuration from `$XDG_CONFIG_HOME/anechoic/runtime.toml`, or `~/.config/anechoic/runtime.toml` when unset. Its exact schema is:

```toml
schema_version = 1

[shared_mcp]
projects_root = "/Users/am/Documents/My_Repos"
http_port = 8092
max_loaded_projects = 2
```

`max_loaded_projects` is optional and defaults to 2. `projects_root` is a canonical host directory outside every Project, not Project Settings. Mount it read/write. The mount grants no cross-Project authority and does not provide OS-level hostile-workload isolation. `http_port` is the configurable host-published port. The image listens on 8092; do not hard-code historical host port 56317. Host-config changes require restart and never remap a live Project root.

The canonical installer is `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/INSTALL_TOOLS/install.py`. Its `runtime` and `project` commands default to dry-run and require `--apply` for effects. `runtime` writes only global Docker parameters `projects_root`, `http_port`, and `max_loaded_projects` in host TOML outside all Projects.

`runtime --harness=codex` may copy the standard-library hook and create its isolated host environment under `XDG_DATA_HOME/anechoic/runtime`, outside `projects_root`. It may register one global hook and loopback HTTP MCP connection while preserving unrelated host configuration. A conflicting ANECHOIC connection refuses before effects. With `--apply`, an optional immutable `sha256:<64 lowercase hex>` image delegates start and readiness to the existing shared launcher. Without an image, report configuration only and no running container. This does not grant trust or claim activation.

`project` targets only the selected directory. A fresh Project requires an explicit prefix and receives only minimal settings, a control root, and empty structure. An existing prefix, configuration, and structure remain authoritative. Install the canonical thin Skill bundled in the release. Do not install copied Tools, initialize Git, or change Docker, global MCP, or global hooks. Refuse missing, ambiguous, unsafe, or conflicting preconditions before effects. Roll back own writes without overwriting concurrent edits.

### Binding, frontier, and state

Eagerly discover a bounded candidate Project set below the configured canonical non-symlink `projects_root`. Admit only an existing canonical non-symlink Project directory strictly below it, with declarations for its authoritative prefix, control root, and full opaque identity. Reject outside, missing, symlink-substituted, ambiguous, or undeclared roots. Never infer a Project from a prefix, ambient working directory, Git ancestor, parent, sibling, or global `current_project`.

Bind before provider dispatch. Carry outer `project_root`, prefix, control root, full opaque identity, and binding revision with the unchanged native request through Tool calls, nested and asynchronous work, results, receipts, and diagnostics. Use the same absolute host/container root without translation; otherwise retain the admitted mapping revision. Use root-per-call context and a ProjectGateway child keyed by full identity; do not introduce a global selector. Recheck the frozen binding at existing freshness and effect boundaries; never silently switch mappings.

Load or reuse only the bound Project's applicable sources, settings, model generation, native Tool frontier, DBOS, Git, Journal, locks, caches, and result paths. Keep mutable state and outputs at their actual owners. Bound loaded contexts by `max_loaded_projects`; accessible Project count is not loaded count. Evict only idle contexts. Refuse busy admission and do not retry, replay, or select another Project automatically.

Publish the shared Tool frontier under AN-S-1895.

Allow lazy discovery of a new or nested Project only for an already advertised compatible Tool name. A new Tool name requires explicit shared-service restart and client reconnect; do not assume `tools/list_changed`.

### Health, ownership, and evidence

Runtime Setup (C65) owns machine-local host settings; Backend (C45) validates them and owns the shared Project catalog, routing, and pool; MCP (C21) owns HTTP transport and launcher. Deliver the configured repository mount and Project-local Skill.

Host-shared health is ready only after service initialization and publication of the frontier, not after every Project job or cache loads. Show known Project contexts with prefix and opaque identity separately; unloaded or unknown Projects remain unknown. Keep the configured loopback listener, default JSON `ready` boolean, 200/503 semantics, and escaped HTML. Health is read-only: no controls, dispatch, polling, reload, mutation, replay, raw payloads, credentials, provider exception text, or absolute paths. Host startup and unbound events have no invented Project prefix; request logs use the bound prefix.

Record shared MCP delivery evidence under AN-S-5185.

Keep the legacy one-Project launcher as a separate mode until independently authorized adoption. Its selection records do not restrict the shared per-request runtime. This requirement changes no native Tool meaning and authorizes no deployment, production replacement, home-config write, active-runtime claim, or acceptance claim.

Stop the affected call for invalid host config, an outside, symlink-substituted or ambiguous root, missing declaration, stale mapping, unavailable or busy pool admission, or conflicting Tool contract. Do not select another Project, change a native Tool contract, retry, or replay uncertain work.
