# Shared host MCP handoff

One external Streamable HTTP MCP service can serve configured Projects through
the retained native Workbench Tool surface.

## Host settings

Settings live outside any Project. With no explicit `--host-settings` argument,
the loader reads `$XDG_CONFIG_HOME/anechoic/runtime.toml`, or
`~/.config/anechoic/runtime.toml` when `XDG_CONFIG_HOME` is unset:

```toml
schema_version = 1

[shared_mcp]
projects_root = "/Users/am/Documents/My_Repos"
http_port = 8092
max_loaded_projects = 2
```

`projects_root` is the host root containing the configured Projects. Use
`project_root` in its place to mount and serve one repository. See the
[Runtime Setup example](../../../../LAYER_6_RUNTIME_SETUP/runtime.example.toml) and
[install guide](../../../../INSTALL.md) for Project creation defaults. The
`max_loaded_projects` value bounds warm in-memory contexts; it does not limit
which Projects under the configured root may be addressed.

The container has exactly two application bind mounts: the configured host
Projects root at the same absolute path, read/write, and this host settings file
at the same absolute path, read-only. There is no `/project` remapping, Docker
socket, or home-directory volume. This is an application boundary, not
operating-system or adversarial isolation.

The named volume `anechoic-framework-db` mounts at `/var/lib/anechoic` inside
the container. The runtime rebuilds its database when the delivered Active
Meta-Ontology or Meta-Methodology Atoms change. Workbench SQL can read those
Atoms through `framework.atoms`. Project Atoms and Journal data remain scoped
to the Project.

## Dry-run and explicit start

The launcher requires an explicit immutable image reference (`sha256:` followed
by 64 lowercase hexadecimal characters). It never builds an image or guesses a
tag. The default action is a Docker-free dry-run that prints the validated
Compose command and explicit `ANECHOIC_*` settings. Inherited Docker client
environment remains internal to the subprocess and is not printed. From the
repository root, using the selected Python 3.14 environment:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project "$PWD/LAYER_3_ENVIRONMENTS_C72/engine" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group dev python -B \
  LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py \
  --host-settings "${XDG_CONFIG_HOME:-$HOME/.config}/anechoic/runtime.toml" \
  --image sha256:<admitted-image-digest>
```

Append `--apply` only as an explicit operator start after the immutable image
includes the intended source changes and the release gate has passed. Readiness
is reported only after Docker readback verifies the image, mounts, loopback
publication, and `/anechoic/health`; a Docker error or unverified readiness is not a
started/ready claim. No `--apply` invocation is implied by this document.

The shared listener publishes one loopback host port configured by
`shared_mcp.http_port` to container port `8092`, with MCP at `/anechoic/mcp` and health
at `/anechoic/health`. Do not start it on the current production port `56317`; preserve
the legacy runtime there until a coordinated replacement is authorized. Tests
use non-production ports and fakes.

The launcher does not claim a build, deployment, scheduling, stop or cleanup
operation beyond the explicit command requested by its Operator.
