# Shared host MCP handoff

One external Streamable HTTP MCP service can serve configured Projects through
the retained native Workbench Tool surface.

## Host settings

Save the settings at `<mounted_folder>/.anechoic_runtime_config.toml`. The
file's parent is the mounted folder. Supply that folder with
`--mounted-folder` or pass the file with `--host-settings`.

```toml
schema_version = 1

[container]
mode = "projects"
http_port = 7777
max_loaded_projects = 2
log_level = "INFO"
```

`mode = "project"` serves the mounted repository. The `projects` mode serves
repositories under the mounted folder. See the
[Runtime Setup example](../../../../../LAYER_5_USER_SETUP_C65/runtime.example.toml) and
[install guide](../../../../../INSTALL.md) for Project creation defaults. The
`max_loaded_projects` value bounds warm in-memory contexts; it does not limit
which Projects under the configured root may be addressed.

Shared startup reads `container.log_level` and passes it to Studio processes.
Use `DEBUG`, `INFO`, `WARNING`, or `ERROR`. An omitted level uses `INFO`. For a
direct or development start, set `ANECHOIC_LOG_LEVEL` in the launch environment.
The level takes effect when a new runtime process starts. If a direct launcher
reuses a running container, that runtime continues with its original level.

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

Use the saved immutable `container.image` or supply `--image`. An immutable
image ID has `sha256:` followed by 64 lowercase hexadecimal characters. The
default action is a Docker-free dry run that prints the validated
Compose command and explicit `ANECHOIC_*` settings. Inherited Docker client
environment remains internal to the subprocess and is not printed. From the
repository root, using the selected Python 3.14 environment:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group dev python -B \
  LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py \
  --mounted-folder "/absolute/path/to/repositories"
```

Append `--apply` only as an explicit operator start after the immutable image
includes the intended source changes and the release gate has passed. Readiness
is reported only after Docker readback verifies the image, mounts, loopback
publication, and `/anechoic/health`; a Docker error or unverified readiness is not a
started/ready claim. No `--apply` invocation is implied by this document.

The shared listener publishes one loopback host port configured by
`container.http_port` to container port `8092`, with MCP at `/anechoic/mcp` and health
at `/anechoic/health`. Use a separate port from the existing production listener
until a coordinated replacement is authorized. Tests use non-production ports
and fakes.

The launcher does not claim a build, deployment, scheduling, stop or cleanup
operation beyond the explicit command requested by its Operator.
