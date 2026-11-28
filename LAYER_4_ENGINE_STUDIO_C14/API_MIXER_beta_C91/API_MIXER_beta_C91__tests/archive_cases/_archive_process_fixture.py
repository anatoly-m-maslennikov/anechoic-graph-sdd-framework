"""Archive process fixture."""

from hashlib import sha256
import os
import signal
import subprocess
import sys
import threading
import time

import httpx2

from ._archive_sources import ENGINE, INSTANCE, write_ticket


class ArchiveProcessFixture:
    def seed_tickets(self):
        self.current = write_ticket(
            self.tickets,
            "AN-T-2-TASK--active.md",
            "AN-T-2",
            "active",
            2,
            "active",
        )
        write_ticket(
            self.tickets / "01_draft",
            "AN-T-2@3-draft-TASK--draft.md",
            "AN-T-2",
            "draft",
            3,
            "draft",
        )
        write_ticket(
            self.tickets / "09_archived",
            "AN-T-99@4-TASK--archived.md",
            "AN-T-99",
            "archived",
            4,
            "archived",
        )
        self.misplaced = write_ticket(
            self.tickets / "09_archived",
            "AN-T-97-TASK--misplaced.md",
            "AN-T-97",
            "in_queue",
            1,
            "misplaced",
        )
        self.broken = (
            self.tickets / "09_archived" / "AN-T-98@1-TASK--broken.md"
        )
        self.broken.write_text("---\nidentity: [invalid\n", encoding="utf-8")

    def prepare_process(self, manifest):
        self.arguments = [
            "--socket",
            str(self.directory / "api.sock"),
            "--instance-id",
            INSTANCE,
            "--project-root",
            str(self.root),
            "--control-root",
            self.control.name,
            "--manifest-path",
            manifest.relative_to(self.root).as_posix(),
            "--manifest-sha256",
            sha256(manifest.read_bytes()).hexdigest(),
            "--project-prefix",
            "AN",
            "--workbench-storage",
            "memory",
        ]
        self.env = {
            **os.environ,
            "PYTHONPATH": str(ENGINE),
            "ANECHOIC_RUNTIME_PROFILE": "test",
            "ANECHOIC_WORKBENCH_STORAGE": "memory",
            "ANECHOIC_JOURNAL_STORAGE": "files",
            "ANECHOIC_ARCHIVES": "load",
            "ANECHOIC_LOG_LEVEL": "ERROR",
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"),
            ),
        }
        self.processes, self.clients = [], []
        self.held = None
        self.monitor = None
        self.monitor_stop = threading.Event()
        self.addCleanup(self.stop_processes)

    def stop_processes(self):
        self.monitor_stop.set()
        if self.monitor is not None:
            self.monitor.join(timeout=10)
        if self.held is not None:
            try:
                os.kill(self.held, signal.SIGCONT)
            except ProcessLookupError:
                pass
            self.held = None
        for process, log in reversed(self.processes):
            if not process.stdin.closed:
                process.stdin.close()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            log.close()
        for client in self.clients:
            client.close()

    def start(self, module, *extra):
        log = (self.directory / (module.rsplit(".", 1)[-1] + ".log")).open(
            "w+"
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                module,
                *self.arguments,
                *extra,
            ],
            cwd=ENGINE,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=log,
        )
        self.processes.append((process, log))
        return process

    def client(self, name):
        client = httpx2.Client(
            transport=httpx2.HTTPTransport(uds=str(self.directory / name)),
            base_url="http://private",
            trust_env=False,
            timeout=5,
        )
        self.clients.append(client)
        return client

    def wait(self, predicate, process, message, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and process.poll() is None:
            try:
                if value := predicate():
                    return value
            except httpx2.TransportError, KeyError, ValueError:
                pass
            time.sleep(0.03)
        self.fail(f"{message}; exit={process.poll()}")

    def hold_archive(self, owner):
        jobs = self.client("jobs.sock")
        deadline = time.monotonic() + 90
        while (
            not self.monitor_stop.is_set()
            and owner.poll() is None
            and time.monotonic() < deadline
        ):
            if not (self.directory / "jobs.sock").is_socket():
                time.sleep(0.02)
                continue
            try:
                pid = jobs.get("/health").json()["result"]["pid"]
                rows = subprocess.check_output(
                    ["ps", "-eo", "pid=,ppid=,args="], text=True, timeout=2
                ).splitlines()
                for row in rows:
                    parts = row.strip().split(None, 2)
                    if not (
                        len(parts) == 3
                        and int(parts[1]) == pid
                        and "anechoic-archive-" in parts[2]
                    ):
                        continue
                    if self.monitor_stop.is_set():
                        return
                    child = int(parts[0])
                    os.kill(child, signal.SIGSTOP)
                    self.held = child
                    return
            except (
                httpx2.TransportError,
                KeyError,
                ValueError,
                ProcessLookupError,
                subprocess.TimeoutExpired,
            ):
                pass
            time.sleep(0.02)

