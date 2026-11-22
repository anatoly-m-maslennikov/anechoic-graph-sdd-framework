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


def _snapshot(jobs, instance_id, binding, path):
    response = jobs.post("/jobs/build", json={"instance_id": instance_id, **binding})
    result = response.json()
    if not response.is_success:
        raise RuntimeError("Beta snapshot build failed: " + str(result.get("error", {}).get("message", "")))
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result["result"], stream)


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
    database, orchestrator, snapshot = (path.with_name(name) for name in ("db.sock", "jobs.sock", "snapshot.json"))
    binding = {"root": args.project_root, "control_root": args.control_root, "manifest_path": args.manifest_path,
               "manifest_sha256": args.manifest_sha256, "project_prefix": args.project_prefix}
    with _peer(ORCHESTRATOR, orchestrator, args.instance_id) as jobs:
        _snapshot(jobs, args.instance_id, binding, snapshot)
        try:
            with _peer(DATABASE, database, args.instance_id, "--snapshot", str(snapshot),
                       "--manifest-sha256", args.manifest_sha256):
                snapshot.unlink()
                app = create_app(args.instance_id, args.manifest_sha256, args.project_root, str(database),
                                 str(orchestrator), host_root=args.host_root, blacklist=args.blacklist)
                serve(path, app)
        finally:
            snapshot.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
