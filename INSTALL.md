# Install Anechoic locally

This guide is for a human or an AI agent setting up Anechoic from a supplied framework checkout. Run Setup on macOS, Linux, or in a WSL 2 shell on Windows.

## For an AI agent

Carry out the setup and verify the result. Do not stop after preparing commands. Ask the user for:

- The absolute path of one Project repository, or of a folder containing Project repositories.
- Whether to set up Codex integration, if the request leaves that open.
- For a new single Project only, its name and prefix.

Use the supplied framework checkout as the working directory. Inspect existing configuration before changing it. Preserve existing Project settings and unrelated services. If a required choice is unclear, ask before making that change.

## Prerequisites

- A supplied checkout containing `LAYER_5_USER_SETUP_C65/setup.py` and
  `LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/setup/`.
- Git and `uv` available on the host.
- A running container engine: OrbStack or Docker Desktop on macOS, Docker on
  Linux or WSL 2. The Docker CLI and Compose plugin must be available.
- The Codex CLI, if you select Codex integration.

On Windows, use Docker Desktop in Linux-container mode and enable integration
for the WSL 2 distribution that runs Setup. Use Linux paths for the Framework
checkout and the Project. For a Project on a Windows drive, use its WSL path
such as `/mnt/c/Users/you/repos/project`. Store host settings in the WSL home directory.

[Docker Desktop WSL 2 integration](https://docs.docker.com/desktop/features/wsl/)

Run the command below from the Framework checkout root. It uses managed
Python 3.14 and the locked Setup environment. Setup provisions the
locked Release and Engine environments as needed.

## Install for one Project

Replace the path with the absolute path to the Project repository:

```sh
setup="$PWD/LAYER_5_USER_SETUP_C65"
UV_PROJECT_ENVIRONMENT="$setup/.venv-setup" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/setup" \
    --locked --python 3.14 --managed-python --no-env-file \
    python -B -E "$setup/setup.py" install --project "/absolute/repo" --port 8092
```

For a new Project, add `--init-project --name NAME --prefix PREFIX` with the user's chosen name and prefix. Use these flags only for an explicit new single Project. Existing Projects retain their settings.

To set up multiple Project repositories under one containing folder, use `--projects-root "/absolute/repos"` in place of `--project "/absolute/repo"`. This mounts the containing folder.

## Options

- Use `--engine orbstack|docker` to select the container engine. On macOS,
  OrbStack is the default; use `--engine docker` for Docker Desktop. On Linux
  and WSL 2, Docker is the default. Setup selects the matching Docker context
  for its commands without changing the host's current context.
- Add `--agent codex` (or `--codex`) to install the user-wide hook and register the loopback MCP endpoint. Ask the user to review and trust the hook in Codex with `/hooks`. See the [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks).
- Setup saves startup settings in `.anechoic_runtime_config.toml` at the root of the selected mount. Edit its `[container]` table to set the port, image, Docker context, timeouts, storage defaults, or log level. See the [settings example](LAYER_5_USER_SETUP_C65/runtime.example.toml).
- Add `--host-settings PATH` to select an existing settings file. Setup can also read the earlier `anechoic/runtime.toml` under `XDG_CONFIG_HOME` or `~/.config`.
- For new Projects, select storage with `--workbench-storage disk|memory` and `--journal-storage files|duckdb`. The defaults are `disk` and `files`.

For example, add `--agent codex` to the install command if the user selected Codex. Do not change an existing endpoint or another service automatically to resolve a conflict.

## Verify and repeat

The installer uses the saved immutable image when one is set. On first setup it builds and saves the image ID. The Engine launcher opens an MCP session through the published port and verifies access in single-Project mode. Check for `"outcome": "completed"` in the JSON result.

After the user trusts the hook, start a new Codex session inside a mounted Project repository. The hook sends the nearest Git worktree root, including when Codex starts in a subdirectory. With `--projects-root`, the same hook serves every configured Project under that folder.

Re-run the same command to reuse the configuration. If setup fails, report the failure and resolve it without overwriting existing Project settings or changing unrelated services.

## Upgrade an installed Project

For a prior install with only `anechoic/runtime.toml` under
`XDG_CONFIG_HOME` or `~/.config`, stop the prior shared MCP container
for that Project or Projects root. Check its mounts and port to select
the container. Keep the settings file and Project data.

Rerun Setup from the new checkout with the same Project or Projects
root, configuration directory, and engine. Omit `--port` and the storage
flags to keep their saved values. Setup builds the image and writes its
pin to `.anechoic_runtime_config.toml` in the mounted folder.

If the mounted settings file already exists, use the steps below.

From the new Framework checkout, build the image with
`./release__public build-image --run-id upgrade-v0-5-0`. Pass
`--engine orbstack` or `--engine docker` to match the installed Project.

Set `[container].image` in the mounted settings file to the new image
ID. Run Setup again from the new checkout with the existing Project or
Projects root. Keep the existing port and storage settings.

Check that Setup reports the new image ID. Run an MCP query against
the same Project to verify the upgrade.

Docker keeps the shared Framework database in the `anechoic-framework-db`
volume. Each Project keeps its own database at `.anechoic_runtime/db/project.duckdb`
when its Manifest selects disk-backed Workbench or DuckDB Journal storage.
