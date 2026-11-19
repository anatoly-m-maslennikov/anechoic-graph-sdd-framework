# CA-M-322@13
# CA-R-1820@9

"""MCP entry point for the native Workbench gateway."""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from direct_gateway import DirectGateway, bind_selection, startup_selection
from runtime_process_boundary import run_process

if TYPE_CHECKING:
    from native_query import NativeQueryInputs


def _serve_stdio(args, *, native_inputs: NativeQueryInputs | None = None):
    if native_inputs is not None:
        from native_query import create_native_gateway

        asyncio.run(create_native_gateway(args.project_root, args.control_root, native_inputs).serve())
        return
    selection = startup_selection(args.project_root, args.control_root, args.instance_id, args.host_project_root)
    from native_project_selection import NativeProjectSelection

    if isinstance(selection, NativeProjectSelection):
        from native_query import NativeQueryOwner
        from native_startup import load_native_inputs

        owner = NativeQueryOwner(selection, load_native_inputs(selection))
        asyncio.run(DirectGateway(selection.root, native_query=owner).serve())
    else:
        with bind_selection(selection):
            asyncio.run(DirectGateway(args.project_root, selection=selection).serve())


def main(argv=None, *, native_inputs: NativeQueryInputs | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--control-root')
    parser.add_argument('--instance-id')
    parser.add_argument('--host-project-root')
    parser.add_argument('--transport', choices=('stdio', 'streamable-http'), default='stdio')
    args = parser.parse_args(argv)
    if native_inputs is not None and (
        not args.control_root
        or args.instance_id is not None or args.host_project_root is not None
    ):
        parser.error('Native selection requires --control-root and derives its own instance identity')
    if args.transport == 'stdio':
        return run_process(
            lambda: _serve_stdio(args, native_inputs=native_inputs), operation='mcp.stdio_startup',
            root=args.project_root,
        )
    else:
        from http_server import main as serve_http
        # The HTTP entrypoint owns its process boundary; do not report this delegation twice.
        http_argv = ['--project-root', str(args.project_root)]
        for flag, value in (('--control-root', args.control_root), ('--instance-id', args.instance_id),
                            ('--host-project-root', args.host_project_root)):
            if value is not None:
                http_argv += [flag, value]
        if native_inputs is not None:
            return serve_http(http_argv, native_inputs=native_inputs)
        return serve_http(http_argv)


if __name__ == '__main__':
    raise SystemExit(main())
