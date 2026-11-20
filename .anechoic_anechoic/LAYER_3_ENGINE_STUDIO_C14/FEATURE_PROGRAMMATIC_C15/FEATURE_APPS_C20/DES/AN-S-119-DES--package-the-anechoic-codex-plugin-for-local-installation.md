---
identity:
  atom_id: AN-S-119
context:
  container:
    component: C20
  tier: 1
  lens: DES
state:
  status: active
  version: 23
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Package the ANECHOIC Codex plugin for local installation

# Package the ANECHOIC Codex plugin for local installation

`CODEX_PLUGIN` **must** be one versioned installable package with a stable kebab-case identity, a required `.codex-plugin/plugin.json` manifest, contained relative references **to** **every** bundled skill **and** optional MCP, UI, asset, **or** hook resource, **and** one repository-local marketplace entry through which Codex can discover **and** install the package. Credentials **and** mutable runtime state **must** remain outside the package, **every** declared resource **must** resolve **after** installation, **and** the advertised identity, version, description, **and** capabilities **must** match the packaged content.
