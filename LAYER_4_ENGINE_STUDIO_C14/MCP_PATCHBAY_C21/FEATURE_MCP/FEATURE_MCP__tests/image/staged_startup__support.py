"""Test-owned archive pause and read-only peer probes for packaged startup."""
from hashlib import sha256
import json
import subprocess
from time import monotonic, sleep
from uuid import uuid4

from ..FEATURE_MCP__tests__shared import CONTROL, project
from ..workbench_docker_support import defer_container_cleanup, docker_deadline_env, image_timeout, observing

_BARRIER = r'''
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
'''
_WRAPPER = '''import os,subprocess,sys
subprocess.Popen([sys.executable,'-B','-c',%r],start_new_session=True)
os.execv(sys.executable,[sys.executable,'-B','/workspace/LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py','mcp-http'])
''' % _BARRIER
_RPC = r'''
import glob,http.client,json,os,socket,sys
name,method,path,body=sys.argv[1:]
paths=glob.glob('/tmp/ane-beta-host-*/'+name)
if len(paths)!=1: raise SystemExit('peer sockets '+str(paths))
class U(http.client.HTTPConnection):
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); self.sock.connect(paths[0])
c=U('localhost'); c.request(method,path,body or None,{'Content-Type':'application/json'})
r=c.getresponse(); payload=json.loads(r.read()); print(json.dumps({'status':r.status,'body':payload}))
'''
_DB = r'''
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
'''


def prepare(root):
    project(root)
    manifest, = root.glob('*PROJECT_MANIFEST--*.md')
    manifest.write_text(manifest.read_text().replace("'storage': 'memory'", "'storage': 'disk'"))
    control = root / CONTROL
    directory = control / '__TICKETS' / 'TASKS'
    archive = directory / '09_archived'
    archive.mkdir(parents=True)
    for i in range(4):
        (directory / f'AN-T-{i + 1}-TASK--staged.md').write_text(carrier(i + 1, 'active', f'Current {i + 1}'))
    for i in range(1500):
        (archive / f'AN-T-{10000 + i}@1-TASK--history.md').write_text(carrier(10000 + i, 'archived', 'History'))
    return directory


def carrier(number, status, summary):
    return (f'---\nidentity: {{atom_id: AN-T-{number}}}\ncontext: {{container: {{component: C00}}}}\n'
            f'state: {{status: {status}, version: 1}}\n---\n\n## Summary\n\n{summary}\n')


class PackagedProbe:
    def __init__(self, case, root, image):
        self.case, self.root = case, root
        self.instance = sha256(f"{root.resolve(strict=True)}\0{CONTROL}".encode()).hexdigest()
        name = 'anechoic-staged-' + uuid4().hex
        defer_container_cleanup(case.addCleanup, name)
        self.started = monotonic()
        self.container = self.docker('run', '--detach', '--pull=never', '--init', '--read-only', '--name', name,
            '--label', 'anechoic.test=staged-startup', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
            '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m', '--pids-limit', '128', '--cpus', '1',
            '--publish', '127.0.0.1::8092', '--mount', f'type=bind,src={root},dst=/project',
            '--env', 'ANECHOIC_RUNTIME_NAMESPACE=docker', '--env', f'ANECHOIC_CONTROL_ROOT={CONTROL}',
            '--env', f'ANECHOIC_PROJECT_INSTANCE_ID={self.instance}', '--env', f'ANECHOIC_HOST_PROJECT_ROOT={root}',
            '--env', docker_deadline_env(),
            '--entrypoint', '/opt/venv/bin/python', image, '-B', '-c', _WRAPPER, timeout=45)
        self.refresh_binding('cold')

    def refresh_binding(self, phase):
        binding = self.docker('port', self.container, '8092/tcp')
        self.case.assertRegex(binding, r'\A127\.0\.0\.1:[0-9]+\Z')
        self.url = 'http://' + binding
        self.phase(phase + '_binding', binding=binding)

    def phase(self, name, **details):
        print('ANECHOIC_STAGED_PHASE ' + json.dumps({'phase': name, **details}), flush=True)

    def docker(self, *args, timeout=10):
        result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=image_timeout(timeout))
        if result.returncode:
            raise subprocess.CalledProcessError(result.returncode, ['docker', *args], result.stdout, result.stderr)
        return result.stdout + result.stderr if args[0] == 'logs' else result.stdout.strip()

    def until(self, func, label):
        deadline = monotonic() + 420
        while observing(self.container, deadline):
            try:
                result = func()
                if result:
                    return result
            except (OSError, ValueError, subprocess.SubprocessError, KeyError):
                pass
            sleep(.2)
        self.case.fail('Timed out waiting for ' + label)

    def exec(self, code, *args):
        return self.docker('exec', self.container, '/opt/venv/bin/python', '-B', '-c', code, *args)

    def peer(self, socket_name, method, route, body=None):
        value = json.loads(self.exec(_RPC, socket_name, method, route, '' if body is None else json.dumps(body)))
        if value['status'] != 200:
            raise ValueError(str(value))
        return value['body']['result']

    def health(self):
        return self.peer('db.sock', 'GET', '/health')

    def jobs(self):
        return self.peer('jobs.sock', 'GET', '/jobs/worker-runs?instance_id=' + self.instance)

    def rows(self, sql):
        return self.peer('db.sock', 'POST', '/database', {'instance_id': self.instance, 'sql': sql})['rows']

    def stopped(self):
        marker = self.exec("from pathlib import Path; p=Path('/tmp/staged-archive-pid'); print(p.read_text() if p.exists() else '')")
        health, jobs = self.health(), self.jobs()
        latest, archive = jobs.get('latest') or {}, jobs.get('archive') or {}
        if latest.get('state') in ('failed', 'aborted') and not latest.get('retrying'):
            raise RuntimeError('Startup failed before archive barrier: ' + json.dumps(latest))
        if archive.get('state') in ('failed', 'aborted'):
            raise RuntimeError('Archive failed before barrier: ' + json.dumps(archive))
        if archive.get('state') == 'succeeded' or (latest.get('state') == 'succeeded'
                and health.get('ready') and not health.get('archive_pending')):
            raise RuntimeError('Archive completed before barrier: ' + json.dumps(archive))
        return marker

    def release(self):
        self.exec("import os,signal; from pathlib import Path; p=Path('/tmp/staged-archive-pid'); os.kill(int(p.read_text()),signal.SIGCONT); p.unlink()")

    def disk(self):
        return json.loads(self.exec(_DB))

    def ready(self):
        health, jobs = self.health(), self.jobs()
        latest = jobs.get('latest') or {}
        if latest.get('state') == 'failed' and not latest.get('retrying'):
            raise RuntimeError(str(latest))
        return (health, jobs) if health['ready'] and latest.get('state') == 'succeeded' else None

    def complete(self):
        health, jobs = self.health(), self.jobs()
        archive = jobs.get('archive') or {}
        if archive.get('state') in ('failed', 'aborted'):
            raise RuntimeError(str(archive))
        return (health, jobs) if not health['archive_pending'] and archive.get('state') == 'succeeded' else None
