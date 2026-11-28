"""Test-owned archive pause and read-only peer probes for packaged startup."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
from time import monotonic, sleep
from uuid import uuid4

from ..FEATURE_MCP__tests__shared import (
    CONTROL,
    project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.integration.\
    workbench.group_4.workbench_docker_support import (
    defer_container_cleanup,
    docker_deadline_env as docker_deadline_env,
    image_timeout,
    observing,
)

from .staged_startup_timing__support import (
    started_at_ns as started_at_ns,
    startup_events as startup_events,
    scan_durations as scan_durations,
    timing_summary as timing_summary,
    cold_throughput as cold_throughput,
    startup_outcome as startup_outcome,
)
from .staged_startup_probe__support import ProbeStatus


_BARRIER = r"""
import os,signal,time
from pathlib import Path
while True:
 for p in Path('/proc').glob('[0-9]*/cmdline'):
  try: args=[os.fsdecode(x) for x in p.read_bytes().split(b'\0')]
  except OSError: continue
  if '--generation-dir' in args and any('/anechoic-archive-' in x for x in args):
   pid=int(p.parent.name)
   try: os.kill(pid,signal.SIGSTOP)
   except ProcessLookupError: continue
   Path('/tmp/staged-archive-pid').write_text(str(pid)); raise SystemExit
 time.sleep(.01)
"""
_WRAPPER = (
    """import os,subprocess,sys
subprocess.Popen([sys.executable,'-B','-c',%r],start_new_session=True)
os.execv(sys.executable,[sys.executable,'-B','/workspace/LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py','mcp-http'])
"""
    % _BARRIER
)
_RPC = r"""
import glob,http.client,json,os,socket,sys
name,method,path,body=sys.argv[1:]
paths=glob.glob('/tmp/ane-beta-host-*/'+name)
if len(paths)!=1: raise SystemExit('peer sockets '+str(paths))
class U(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); self.sock.connect(paths[0])
c=U('localhost'); c.request(method,path,body or None,{'Content-Type':'application/json'})
r=c.getresponse(); payload=json.loads(r.read()); print(json.dumps({'status':r.status,'body':payload}))
"""
_DB = r"""
import json,os
from pathlib import Path
found=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try: args=[os.fsdecode(x) for x in p.read_bytes().split(b'\0')]
 except OSError: continue
 if '--database-path' in args and any('DATABASE_SERVER_beta_C71__shared' in x for x in args):
  found.append(args[args.index('--database-path')+1])
if len(found)!=1: raise SystemExit('disk database paths: '+str(found))
p=Path(found[0]); s=p.stat(); print(json.dumps([str(p),s.st_dev,s.st_ino]))
"""


def prepare(root, *, write_carrier=None):
    write_carrier = carrier if write_carrier is None else write_carrier
    project(root)
    (manifest,) = root.glob("*PROJECT_MANIFEST--*.md")
    manifest.write_text(
        manifest.read_text().replace(
            "'storage': 'memory'", "'storage': 'disk'"
        )
    )
    control = root / CONTROL
    directory = control / "__TICKETS" / "TASKS"
    archive = directory / "09_archived"
    archive.mkdir(parents=True)
    for i in range(4):
        (directory / f"AN-T-{i + 1}-TASK--staged.md").write_text(
            write_carrier(i + 1, "active", f"Current {i + 1}")
        )
    for i in range(1500):
        (archive / f"AN-T-{10000 + i}@1-TASK--history.md").write_text(
            write_carrier(10000 + i, "archived", "History")
        )
    return directory


def carrier(number, status, summary):
    return (
        f"---\nidentity: {{atom_id: AN-T-{number}}}\ncontext: {{container: {{component: C00}}}}\n"
        f"state: {{status: {status}, version: 1}}\n---\n\n## Summary\n\n{summary}\n"
    )


def canonical_carrier(number, status, summary):
    return (
        f"---\natom_family: TKT\natom_id: AN-T-{number}\ncontainer: {{component: C00}}\npriority: 2\n"
        f"context: {{template: task}}\nstate: {{status: {status}, version: 1, "
        "updated_at: '2026-11-23T00:00:00Z'}\n---\n\n## Summary\n\n"
        + summary
        + "\n"
    )


class PackagedProbe(ProbeStatus):
    def __init__(self, case, root, image):
        self.case, self.root = case, root
        self.instance = sha256(
            f"{root.resolve(strict=True)}\0{CONTROL}".encode()
        ).hexdigest()
        name = "anechoic-staged-" + uuid4().hex
        defer_container_cleanup(case.addCleanup, name)
        self.started = monotonic()
        self.container = self.start_container(root, image, name)
        self.start_time("cold")
        self.refresh_binding("cold")

    def start_time(self, phase):
        value = self.docker(
            "inspect", "--format", "{{.State.StartedAt}}", self.container
        )
        if not hasattr(self, "starts"):
            self.starts = {}
        self.starts[phase] = value

    def timing(self, phase):
        start = self.starts[phase]
        logs = self.docker("logs", self.container, timeout=30)
        return timing_summary(logs, start)

    def resources(self):
        source = (
            Path(__file__)
            .with_name("startup_resources__support.py")
            .read_text()
        )
        return json.loads(self.exec(source))

    def startup(self, phase):
        since = started_at_ns(self.starts[phase]) / 1_000_000_000
        return startup_outcome(
            self.rows(
                "SELECT run_id, kind, name, outcome, CAST(detail AS VARCHAR) "
                "FROM flow_events WHERE component = 'C68' "
                f'AND "at" >= {since:.9f} ORDER BY "at", sequence LIMIT 512'
            )
        )

    def restart(self, phase):
        started = monotonic()
        self.docker("start", self.container, timeout=60)
        self.start_time(phase)
        self.refresh_binding(phase)
        return started

    def stop(self):
        grace = "-1" if image_timeout(30) is None else "30"
        self.docker("stop", "--time", grace, self.container, timeout=60)
        status = self.docker(
            "inspect", "--format", "{{.State.ExitCode}}", self.container
        )
        self.case.assertEqual(
            "0",
            status,
            "Expected a clean candidate shutdown before restarting",
        )

    def supports_timing(self):
        return (
            self.exec(
                (
                    "from pathlib import Path; print(int(Path('/workspace/"
                    "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/"
                    "FEATURE_TOOLS/ADAPTERS_C30/startup_timing.py')."
                    "is_file()))"
                )
            )
            == "1"
        )

    def assert_timing(self, phase):
        result = self.timing(phase)
        self.case.assertFalse(
            result["unobserved"], f"{phase} startup timing: {result}"
        )
        self.case.assertFalse(
            result["not_applicable"], f"{phase} startup timing: {result}"
        )
        scan_modes = (
            {"foreground_capture"}
            if phase == "cold"
            else {"foreground_capture", "foreground_hashes"}
        )
        self.case.assertTrue(
            any(
                event.get("phase") == "scan_metrics"
                and event.get("mode") in scan_modes
                and "scan_seconds" in event
                for event in result["events"]
            ),
            f"{phase} foreground scan timing: {result}",
        )
        return result

    def refresh_binding(self, phase):
        binding = self.docker("port", self.container, "8092/tcp")
        self.case.assertRegex(binding, r"\A127\.0\.0\.1:[0-9]+\Z")
        self.url = "http://" + binding
        self.phase(phase + "_binding", binding=binding)

    def phase(self, name, **details):
        print(
            "ANECHOIC_STAGED_PHASE " + json.dumps({"phase": name, **details}),
            flush=True,
        )

    def docker(self, *args, timeout=10):
        result = subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            timeout=image_timeout(timeout),
        )
        if result.returncode:
            raise subprocess.CalledProcessError(
                result.returncode,
                ["docker", *args],
                result.stdout,
                result.stderr,
            )
        return (
            result.stdout + result.stderr
            if args[0] == "logs"
            else result.stdout.strip()
        )

    def until(self, func, label):
        deadline = monotonic() + 420
        while observing(self.container, deadline):
            try:
                result = func()
                if result:
                    return result
            except OSError, ValueError, subprocess.SubprocessError, KeyError:
                pass
            sleep(0.2)
        self.case.fail("Timed out waiting for " + label)

    def exec(self, code, *args):
        return self.docker(
            "exec",
            self.container,
            "/opt/venv/bin/python",
            "-B",
            "-c",
            code,
            *args,
        )

    def peer(self, socket_name, method, route, body=None):
        value = json.loads(
            self.exec(
                _RPC,
                socket_name,
                method,
                route,
                "" if body is None else json.dumps(body),
            )
        )
        if value["status"] != 200:
            raise ValueError(str(value))
        return value["body"]["result"]
