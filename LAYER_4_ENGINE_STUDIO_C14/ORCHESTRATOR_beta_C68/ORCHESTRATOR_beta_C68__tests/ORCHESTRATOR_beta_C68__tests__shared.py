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
from contextlib import closing, contextmanager
from hashlib import sha256
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from unittest.mock import patch

from pydantic import BaseModel

from ..ORCHESTRATOR_beta_C68__shared import GenerationJobs

ENGINE = Path(__file__).resolve().parents[2]


def restore_reuse(jobs, generation):
    witness = {"base_generation": generation, "inputs": {}, "graph_config": None, "endpoints": {},
               "checkpoint_scope": "foreground"}
    with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection") as connection, patch.object(jobs, "_watch_queue"):
        response = connection.return_value.getresponse.return_value
        response.status = 200
        response.read.return_value = json.dumps({"result": witness}).encode()
        jobs._watch()


class RunFixture(BaseModel):
    state: str = "running"
    started_at: float = 0.0
    run_id: str | None = None
    finished_at: float | None = None
    message: str | None = None


def project_jobs(root, *, watch_code=False, database_socket="socket"):
    binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
               "manifest_sha256": "a" * 64, "project_prefix": "AN"}
    return GenerationJobs("test", binding, database_socket, watch_code=watch_code)


def lifecycle_job(jobs, name, arguments):
    request = jobs.binding | {"instance_id": jobs.instance_id, "name": name, "arguments": arguments}
    with (patch.object(jobs, "_await_lifecycle", side_effect=lambda job: job),
          patch.object(jobs.watcher.queue, "put")):
        return jobs.lifecycle(request)


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
    def do_GET(self):
        if self.path.startswith("/spec-snapshot?"):
            self.reply(200, {"result": self.server.spec_snapshot})
            return
        self.reply(409 if self.path.startswith("/model?") else 404, {})

    def do_PUT(self):
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if self.path == "/spec-snapshot":
            self.server.spec_snapshot = {"snapshot_id": "test-snapshot", "rows": payload["rows"]}
            self.reply(200, {"result": {"snapshot_id": "test-snapshot"}})
            return
        if self.path == '/ingestion/issues':
            self.send_response(200)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
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
        self.reply(status, response)

    def reply(self, status, response, headers=()):
        body = json.dumps(response).encode()
        self.send_response(status)
        self.send_header('Content-Length', str(len(body)))
        for name, value in headers:
            self.send_header(name, value)
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


@contextmanager
def kernel_server(root, handler=Kernel):
    with Server(str(root / 'kernel.sock'), handler) as kernel:
        kernel.generations = []
        kernel.payloads = []
        kernel.paths = []
        thread = threading.Thread(target=kernel.serve_forever)
        thread.start()
        try:
            yield kernel
        finally:
            kernel.shutdown()
            thread.join()


class Connection(http.client.HTTPConnection):
    def __init__(self, path, timeout=2):
        super().__init__('localhost', timeout=timeout)
        self.path = str(path)

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def request_json(path, method, endpoint, payload=None, *, timeout=2):
    with closing(Connection(path, timeout=timeout)) as connection:
        connection.request(method, endpoint, None if payload is None else json.dumps(payload))
        response = connection.getresponse()
        return response.status, json.load(response)


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
def watch_project(root, *, watch_code=False, skip_archives=False):
    control, manifest = project(root)
    (control / '__TKT').mkdir()
    binding = {'root': str(root), 'control_root': control.name, 'manifest_path': manifest.name,
               'manifest_sha256': sha256(manifest.read_bytes()).hexdigest(), 'project_prefix': 'AN'}
    binding_file = root / 'binding.json'
    binding_file.write_text(json.dumps(binding))
    with kernel_server(root) as kernel:
        socket_path = root / 'orch.sock'
        env = {**os.environ, 'PYTHONPATH': str(ENGINE)}
        command = [sys.executable, '-B', '-P', '-m', 'ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared',
                   '--socket', str(socket_path), '--instance-id', 'test', '--binding-file', str(binding_file),
                   '--database-socket', str(root / 'kernel.sock')]
        if watch_code:
            command.append('--watch-code')
        if skip_archives:
            command.append('--skip-archives')
        with subprocess.Popen(command, cwd=ENGINE, env=env) as process:
            try:
                wait_for(lambda: (latest(socket_path) or {}).get('generation') == '1', process)
                yield control, manifest, socket_path, kernel, process
            finally:
                process.terminate()
                process.wait(timeout=10)
