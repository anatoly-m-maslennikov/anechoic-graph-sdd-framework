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
- Docker installed and running.
- The Codex CLI, if you select Codex integration.

On Windows, use Docker Desktop in Linux-container mode and enable integration
for the WSL 2 distribution that runs Setup. Use Linux paths for the Framework
checkout and the Project. For a Project on a Windows drive, use its WSL path
such as `/mnt/c/Users/you/repos/project`. Store host settings in the WSL home directory.

[Docker Desktop WSL 2 integration](https://docs.docker.com/desktop/features/wsl/)

Run the command below from the Framework checkout root. It uses managed Python 3.14 and a standard-library-only Setup environment. Setup provisions the locked Release and Engine environments as needed.

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

- Add `--agent codex` (or `--codex`) to install the user-wide hook and register the loopback MCP endpoint. Ask the user to review and trust the hook in Codex with `/hooks`. See the [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks).
- Add `--host-settings PATH` to select a settings file. By default, it is `anechoic/runtime.toml` under `XDG_CONFIG_HOME`, or `~/.config/anechoic/runtime.toml` when `XDG_CONFIG_HOME` is unset. See the [settings example](LAYER_5_USER_SETUP_C65/runtime.example.toml).
- Set `level` in `[logging]` to choose the machine-wide Studio log level for the next Shared runtime launch. Accepted values are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. The default is `INFO`.
- For new Projects, select storage with `--workbench-storage disk|memory` and `--journal-storage files|duckdb`. The defaults are `disk` and `files`.

For example, add `--agent codex` to the install command if the user selected Codex. Do not change an existing endpoint or another service automatically to resolve a conflict.

## Verify and repeat

The installer builds an immutable image. The Engine launcher opens an MCP session from the host through the published port. In single-Project mode it also verifies access to that Project. Check for `"outcome": "completed"` in the JSON result. Report the selected folder and MCP endpoint.

After the user trusts the hook, start a new Codex session inside a mounted Project repository. The hook sends the nearest Git worktree root, including when Codex starts in a subdirectory. With `--projects-root`, the same hook serves every configured Project under that folder.

Re-run the same command to reuse the configuration. If setup fails, report the failure and resolve it without overwriting existing Project settings or changing unrelated services.

Docker keeps the shared Framework database in the `anechoic-framework-db`
volume. Each Project keeps its own database at `.anechoic_runtime/db/project.duckdb`
when its Manifest selects disk-backed Workbench or DuckDB Journal storage.
