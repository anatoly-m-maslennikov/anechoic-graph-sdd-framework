# Install Anechoic locally

This guide is for a human or an AI agent setting up Anechoic from a supplied framework checkout. Run the commands on macOS or Linux. The host launcher currently requires a POSIX environment.

## For an AI agent

Carry out the setup and verify the result. Do not stop after preparing commands. Ask the user for:

- The absolute path of one Project repository, or of a folder containing Project repositories.
- Whether to set up Codex integration, if the request leaves that open.
- For a new single Project only, its name and prefix.

Use the supplied framework checkout as the working directory. Inspect existing configuration before changing it. Preserve existing Project settings and unrelated services. If a required choice is unclear, ask before making that change.

## Prerequisites

- A supplied checkout containing `RUNTIME_SETUP/setup.py` and its locked dependencies.
- Git and `uv` available on the host.
- Docker installed and running.
- The Codex CLI, if you select Codex integration.

The command below uses `uv` to provide managed Python 3.14 and an isolated environment in the checkout. Run it from the root of the framework checkout.

## Install for one Project

Replace the path with the absolute path to the Project repository:

```sh
UV_PROJECT_ENVIRONMENT="$PWD/.anechoic_runtime/setup-venv" uv run --project "$PWD" --locked --python 3.14 --managed-python --no-env-file --group rmed-workflow-mcp python -B RUNTIME_SETUP/setup.py install --project "/absolute/repo" --port 8092
```

For a new Project, add `--init-project --name NAME --prefix PREFIX` with the user's chosen name and prefix. Use these flags only for an explicit new single Project. Existing Projects retain their settings.

To set up multiple Project repositories under one containing folder, use `--projects-root "/absolute/repos"` in place of `--project "/absolute/repo"`. This mounts the containing folder.

## Options

- Add `--agent codex` (or `--codex`) to install the user-wide hook and register the loopback MCP endpoint. Ask the user to review and trust the hook in Codex with `/hooks`. See the [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks).
- Add `--settings PATH` to select a settings file. By default, it is `anechoic/runtime.toml` under `XDG_CONFIG_HOME`, or `~/.config/anechoic/runtime.toml` when `XDG_CONFIG_HOME` is unset. See the [settings example](RUNTIME_SETUP/runtime.example.toml).
- For new Projects, select storage with `--workbench-storage disk|memory` and `--journal-storage files|duckdb`. The defaults are `disk` and `files`.

For example, add `--agent codex` to the install command if the user selected Codex. Do not change an existing endpoint or another service automatically to resolve a conflict.

## Verify and repeat

The installer builds an immutable image and initializes an MCP session. In single-Project mode it also verifies access to that Project. Check for `"outcome": "completed"` in the JSON result. Report the selected folder and MCP endpoint.

After the user trusts the hook, start a new Codex session inside a mounted Project repository. The hook sends the nearest Git worktree root, including when Codex starts in a subdirectory. With `--projects-root`, the same hook serves every configured Project under that folder.

Re-run the same command to reuse the configuration. If setup fails, report the failure and resolve it without overwriting existing Project settings or changing unrelated services.
