"""Parse the runtime setup command line."""

import argparse
from pathlib import Path
import sys


def _configure_project_options(install):
    target = install.add_mutually_exclusive_group()
    target.add_argument("--project", type=Path, help="mount one repository")
    target.add_argument(
        "--projects-root", type=Path, help="mount a directory of repositories"
    )
    install.add_argument(
        "--settings",
        "--host-settings",
        type=Path,
        help="host runtime.toml file",
    )
    install.add_argument(
        "--port",
        type=int,
        help="loopback HTTP port, defaults to 8092 for new settings",
    )
    install.add_argument("--workbench-storage", choices=("disk", "memory"))
    install.add_argument("--journal-storage", choices=("files", "duckdb"))


def parse_arguments(
    argv: list[str] | None, description: str | None
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    commands = parser.add_subparsers(required=True)
    install = commands.add_parser(
        "install", help="build and start the local runtime"
    )
    install.add_argument(
        "--engine",
        choices=("orbstack", "docker"),
        default="orbstack" if sys.platform == "darwin" else "docker",
        help="container engine (default: %(default)s)",
    )
    _configure_project_options(install)
    install.add_argument(
        "--init-project",
        action="store_true",
        help="initialize a new single Project",
    )
    install.add_argument("--name", help="name for a new Project")
    install.add_argument(
        "--prefix", help="identifier prefix for a new Project"
    )
    agent = install.add_mutually_exclusive_group()
    agent.add_argument("--agent", choices=("codex",))
    agent.add_argument(
        "--codex",
        action="store_const",
        const="codex",
        dest="agent",
        help="install the Codex integration",
    )
    result = parser.parse_args(argv)
    if result.init_project and not (result.name and result.prefix):
        parser.error("--init-project requires --name and --prefix")
    if not result.init_project and (result.name or result.prefix):
        parser.error("--name and --prefix require --init-project")
    return result
