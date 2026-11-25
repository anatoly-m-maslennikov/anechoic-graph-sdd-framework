"""Replay the historical canary's bounded MCP coupling contract."""
import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

SOURCE = 'LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION/release_canary.py'
def model(root):
    tree = ast.parse((root / SOURCE).read_bytes())
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def function(name):
        matches = [n for n in functions if n.name == name]
        if len(matches) != 1:
            raise ValueError(f'expected one {name} implementation')
        return matches[0]

    def calls(node, expression):
        return [n for n in ast.walk(node) if isinstance(n, ast.Call) and ast.unparse(n) == expression]

    verify = function('_verify_candidate_image')
    public = function('verify_candidate_image')
    verify_text = ast.unparse(verify)
    if not calls(public, '_verify_candidate_image(root, selection, package, staging, image)') or not all(x in verify_text for x in ("'mcp-http'", "'127.0.0.1::8092'", "'/anechoic/mcp'", "['docker', 'port', container, '8092/tcp']")):
        raise ValueError('unsupported candidate call path')
    imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    backend_imports = [n for n in imports if n.module == 'project_mcp_backend' and any(a.name == 'ProjectMcpBackend' and a.asname is None for a in n.names)]
    backend_references = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == 'ProjectMcpBackend']
    other_backend_import = any(isinstance(n, ast.Import) and any(a.name == 'project_mcp_backend' for a in n.names) or isinstance(n, ast.ImportFrom) and n.module and n.module.endswith('project_mcp_backend') and n not in backend_imports for n in ast.walk(tree))
    if other_backend_import:
        raise ValueError('unsupported backend import')
    if backend_imports or backend_references:
        backend_call = "ProjectMcpBackend(build_if_missing=False).health(base + '/anechoic/mcp', remaining)"
        if len(backend_imports) != 1 or not calls(verify, backend_call) or not calls(tree, 'sys.path.insert(0, str(_DOCKER))'):
            raise ValueError('unsupported backend probe path')
        return True, False
    if not calls(verify, '_mcp_ready(port, deadline - time.monotonic())'):
        raise ValueError('unsupported direct probe call')
    ready = function('_mcp_ready')
    names = {(n.module, a.name, a.asname) for n in ast.walk(ready) if isinstance(n, ast.ImportFrom) for a in n.names}
    if not {('httpx2', 'AsyncClient', None), ('mcp.client.session', 'ClientSession', None), ('mcp.client.streamable_http', 'streamable_http_client', None)} <= names:
        raise ValueError('unsupported MCP client imports')
    check_initializer(ready, calls)
    return False, True


def check_initializer(ready, calls):
    initializers = [n for n in ready.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'initialize']
    if len(initializers) != 1:
        raise ValueError('unsupported initializer')
    init = initializers[0]
    client = [n for n in init.body if isinstance(n, ast.AsyncWith) and len(n.items) == 1 and ast.unparse(n.items[0]) == 'AsyncClient(trust_env=False, follow_redirects=False, timeout=timeout) as client']
    if len(client) != 1:
        raise ValueError('unsupported client context')
    body = client[0].body
    url = [n for n in body if isinstance(n, ast.Assign) and ast.unparse(n) == "url = f'http://127.0.0.1:{port}/anechoic/mcp'"]
    transport = [n for n in body if isinstance(n, ast.AsyncWith) and len(n.items) == 1 and ast.unparse(n.items[0]) == 'streamable_http_client(url, http_client=client) as streams']
    if len(url) != 1 or len(transport) != 1 or body.index(url[0]) > body.index(transport[0]):
        raise ValueError('unsupported loopback MCP transport')
    sessions = [n for n in transport[0].body if isinstance(n, ast.AsyncWith) and len(n.items) == 1 and ast.unparse(n.items[0]) == 'ClientSession(*streams) as session']
    if len(sessions) != 1 or not any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Await) and ast.unparse(n.value.value) == 'session.initialize()' for n in sessions[0].body):
        raise ValueError('unsupported MCP session initialization')
    if not calls(ready, 'asyncio.run(asyncio.wait_for(initialize(), timeout))'):
        raise ValueError('unsupported initialization execution')


def lean_source(backend, direct):
    b, d = str(backend).lower(), str(direct).lower()
    return f'''-- Facts extracted from the recognized Python AST, not runtime observations.\ndef backendImport : Bool := {b}\ndef directMcpInit : Bool := {d}\ndef contract : Bool := !backendImport && directMcpInit\ntheorem checked : contract = {str(not backend and direct).lower()} := by decide\n#eval contract\n'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', type=Path, required=True)
    args = parser.parse_args()
    report = {'findings': [], 'unresolved': []}
    try:
        backend, direct = model(args.checkout.resolve(strict=True))
        with tempfile.TemporaryDirectory() as tmp:
            program = Path(tmp) / 'check.lean'
            program.write_text(lean_source(backend, direct))
            result = subprocess.run([str(args.lean.resolve(strict=True)), str(program)], capture_output=True, text=True, timeout=120, check=False)
        expected = str(not backend and direct).lower()
        if result.returncode or result.stdout.strip().splitlines()[-1:] != [expected]:
            raise ValueError(f'Lean verification failed: {result.stdout} {result.stderr}')
        if backend or not direct:
            report['findings'].append({'path': SOURCE, 'detail': 'Candidate MCP readiness depends on an Engine backend import instead of a release-owned direct MCP initialization.'})
    except (OSError, SyntaxError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        report['unresolved'].append(str(error))
    print(json.dumps(report, sort_keys=True))
    return 2 if report['unresolved'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
