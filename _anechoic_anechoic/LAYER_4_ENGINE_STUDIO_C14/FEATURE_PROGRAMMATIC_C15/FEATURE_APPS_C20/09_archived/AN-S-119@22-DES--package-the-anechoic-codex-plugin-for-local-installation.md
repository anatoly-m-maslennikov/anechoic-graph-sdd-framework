---
atom_family: SPEC
atom_id: AN-S-119
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Package the ANECHOIC Codex plugin for local installation

# Package the ANECHOIC Codex plugin for local installation

`CODEX_PLUGIN` **must** be one versioned installable package with a stable kebab-case identity, a required `.codex-plugin/plugin.json` manifest, contained relative references **to** **every** bundled skill **and** optional MCP, UI, asset, **or** hook resource, **and** one repository-local marketplace entry through which Codex can discover **and** install the package. Credentials **and** mutable runtime state **must** remain outside the package, **every** declared resource **must** resolve **after** installation, **and** the advertised identity, version, description, **and** capabilities **must** match the packaged content.
