"""Reusable Project fixture for Orchestrator process tests."""
import http.client
import json
import os
import socket
import socketserver
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from hashlib import sha256
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[2]



def project(root):
    control = root / '_anechoic_anechoic'
    control.mkdir()
    manifest = root / 'AN-S-1-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
    manifest.write_text(
        '---\natom_family: SPEC\natom_id: AN-S-1\ncontainer:\n  component: C00\ntier: -1\n'
        'context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n'
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nAnechoic\n\n"
        '## Claim\n\n### Formal Claim\n\n```python\n'
        'from anechoic.formal_claims import declare_entity\n'
        'from anechoic.model import ProjectManifest\n'
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n")
    return control, manifest


class Kernel(BaseHTTPRequestHandler):
    def do_PUT(self):
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.payloads.append(payload)
        self.server.paths.append(self.path)
        self.server.generations.append(time.monotonic())
        if self.server.admit_started is not None:
            self.server.admit_started.set()
            self.server.admit_release.wait(30)
        result = {'generation': str(len(self.server.generations))}
        if 'refresh_target' in payload:
            result['result_ids'] = {'old': 'new'}
        status, response = (502 if self.server.reject else 200), {'result': result}
        if self.path == '/generation/native-delta' and self.server.delta_error is not None:
            status, code = self.server.delta_error
            response = {'error': {'code': code}}
        body = json.dumps(response).encode()
        self.send_response(status)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class Server(socketserver.UnixStreamServer):
    generations = None
    payloads = None
    paths = None
    admit_started = None
    admit_release = None
    reject = False
    delta_error = None


class Connection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__('localhost', timeout=2)
        self.path = str(path)

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def wait_for(predicate, process, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and process.poll() is None:
        if predicate():
            return
        time.sleep(0.1)
    raise AssertionError('Orchestrator did not reach expected state')


def latest(path):
    try:
        conn = Connection(path)
        conn.request('GET', '/jobs/worker-runs?instance_id=test')
        result = json.loads(conn.getresponse().read())['result']['latest']
        conn.close()
        return result
    except (OSError, KeyError, http.client.HTTPException):
        return None
    finally:
        conn.close()

@contextmanager
def watch_project(root, *, watch_code=False):
    control, manifest = project(root)
    (control / '__TKT').mkdir()
    binding = {'root': str(root), 'control_root': control.name, 'manifest_path': manifest.name,
               'manifest_sha256': sha256(manifest.read_bytes()).hexdigest(), 'project_prefix': 'AN'}
    binding_file = root / 'binding.json'
    binding_file.write_text(json.dumps(binding))
    with Server(str(root / 'kernel.sock'), Kernel) as kernel:
        kernel.generations = []
        kernel.payloads = []
        kernel.paths = []
        thread = threading.Thread(target=kernel.serve_forever)
        thread.start()
        socket_path = root / 'orch.sock'
        env = {**os.environ, 'PYTHONPATH': str(ENGINE)}
        command = [sys.executable, '-B', '-P', '-m', 'ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared',
                   '--socket', str(socket_path), '--instance-id', 'test', '--binding-file', str(binding_file),
                   '--database-socket', str(root / 'kernel.sock')]
        if watch_code:
            command.append('--watch-code')
        try:
            with subprocess.Popen(command, cwd=ENGINE, env=env) as process:
                try:
                    wait_for(lambda: (latest(socket_path) or {}).get('generation') == '1', process)
                    yield control, manifest, socket_path, kernel, process
                finally:
                    process.terminate()
                    process.wait(timeout=10)
        finally:
            kernel.shutdown()
            thread.join()
