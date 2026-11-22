"""Start the single-Project Beta Backend with independent Kernel and Orchestrator peers."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic, sleep

import httpx2

from .WORKBENCH_BACKEND_beta_C70__pub import create_app, serve, socket_path

ENGINE = Path(__file__).resolve().parents[1]
ORCHESTRATOR = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__pub"
DATABASE = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__pub"


def _stop(peer):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(peer.pid, sig)
        except ProcessLookupError:
            pass
        try:
            peer.wait(timeout=5)
        except subprocess.TimeoutExpired:
            continue
        break
    else:
        peer.wait()


def _wait_for_peer(client, peer, instance_id):
    deadline = monotonic() + 15
    while peer.poll() is None and monotonic() < deadline:
        try:
            response = client.get("/health", timeout=0.5)
        except httpx2.TransportError:
            sleep(0.05)
            continue
        response.raise_for_status()
        result = response.json()["result"]
        if result.get("pid") != peer.pid or result.get("instance_id") != instance_id:
            raise ValueError("Beta peer reported a different Project binding")
        return
    raise RuntimeError("Beta peer did not start")


@contextmanager
def _peer(module, path, instance_id, *args):
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    environment["PYTHONPATH"] = str(ENGINE)
    peer = subprocess.Popen(
        [sys.executable, "-B", "-P", "-m", module, "--socket", str(path), "--instance-id", instance_id, *args],
        cwd=ENGINE, env=environment, stdin=subprocess.DEVNULL, stdout=sys.stderr, start_new_session=True,
    )
    try:
        with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(path)),
                           base_url="http://private", timeout=125, trust_env=False) as client:
            _wait_for_peer(client, peer, instance_id)
            yield client
    finally:
        _stop(peer)


def _wait_for_generation(kernel, jobs, instance_id):
    deadline = monotonic() + 75
    while monotonic() < deadline:
        health = kernel.get("/health", timeout=2)
        health.raise_for_status()
        runs = jobs.get("/jobs/worker-runs", params={"instance_id": instance_id}, timeout=2)
        runs.raise_for_status()
        latest = runs.json()["result"]["latest"]
        if health.json()["result"]["ready"] and latest and latest["state"] == "succeeded":
            return
        if latest and latest["state"] == "failed":
            raise RuntimeError("Initial Beta build failed: " + str(latest.get("message", latest.get("code")))[:2048])
        sleep(0.1)
    raise RuntimeError("Kernel did not admit an initial Beta generation")


def _serve_project(path, args, binding):
    database, orchestrator, binding_file = (path.with_name(name) for name in (
        "db.sock", "jobs.sock", "binding.json"))
    with binding_file.open("x", encoding="utf-8") as stream:
        json.dump(binding, stream)
    try:
        with _peer(DATABASE, database, args.instance_id, "--manifest-sha256", args.manifest_sha256) as kernel:
            with _peer(ORCHESTRATOR, orchestrator, args.instance_id, "--binding-file", str(binding_file),
                       "--database-socket", str(database)) as jobs:
                _wait_for_generation(kernel, jobs, args.instance_id)
                binding_file.unlink()
                app = create_app(args.instance_id, args.manifest_sha256, args.project_root, str(database),
                                 str(orchestrator), host_root=args.host_root, blacklist=args.blacklist)
                serve(path, app)
    finally:
        binding_file.unlink(missing_ok=True)


def _terminate(_signum, _frame):
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("socket", "instance-id", "project-root", "control-root", "manifest-path",
                 "manifest-sha256", "project-prefix"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--host-root")
    parser.add_argument("--blacklist", action="append", default=[])
    args = parser.parse_args()
    path = socket_path(args.socket)
    signal.signal(signal.SIGTERM, _terminate)
    binding = {"root": args.project_root, "control_root": args.control_root, "manifest_path": args.manifest_path,
               "manifest_sha256": args.manifest_sha256, "project_prefix": args.project_prefix}
    _serve_project(path, args, binding)


if __name__ == "__main__":
    main()
