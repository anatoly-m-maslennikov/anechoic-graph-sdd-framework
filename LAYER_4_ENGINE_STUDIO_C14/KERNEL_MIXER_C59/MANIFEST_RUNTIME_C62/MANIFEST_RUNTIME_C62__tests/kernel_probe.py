"""Start the production Kernel process for boundary tests."""

from contextlib import contextmanager
import json
import os
import subprocess
import sys
import time

import httpx2


def write_reviewed_declarations(control, root):
    """Create self-contained carriers from the pinned reviewed Model claims."""
    assets = root / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C51/FEATURE_GENERATED_MODEL_C52"
    ontology = control / "LAYER_1_META_ONTOLOGY_C9"
    ontology.mkdir()
    rows = []
    for name in ("native-graph-claims.json", "native-spec-template-claims.json"):
        rows.extend(json.loads((assets / name).read_text(encoding="utf-8")))
    for number, row in enumerate(rows, 10000):
        subject = row["subject"].replace("PMETA Atom", "Project Config Atom")
        if subject.endswith("//Component Purpose"):
            continue
        claim = row["claim"].replace("PMETA Atom", "Project Config Atom").replace("PMETAAtom", "ProjectConfigAtom")
        claim = claim.replace("from caprmedio.", "from anechoic.")
        if subject.endswith("//Ticket Atom"):
            claim = claim.replace("from typing import ClassVar", "from typing import ClassVar\nfrom dataclasses import field")
            claim = claim.replace("    family_marker: ClassVar[str]", "    label: str | None = field(default=None, kw_only=True, metadata={'allowed_values': ('Task', 'Subtask', 'Sub-epic', 'Epic', 'Version')})\n    family_marker: ClassVar[str]")
        if subject.endswith("//Component Manifest"):
            number = 3109
            claim = claim.replace('tier: int = field(metadata={"allowed_values": (0,)})',
                                  'tier: int = field(metadata={"allowed_values": (1,)})')
        name = "declare-component-manifest" if number == 3109 else f"reviewed-{number}"
        (ontology / f"AN-S-{number}-SPEC--{name}.md").write_text(
            f"---\natom_family: SPEC\natom_id: AN-S-{number}\ntier: 2\ncontainer:\n  component: C9\n"
            f"context:\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n  updated_at: '2026-11-19T00:00:00Z'\n---\n\n"
            f"## Claim scope\n\n{subject}\n\n## Claim\n\n### Formal Claim\n\n```python\n{claim}\n```\n",
            encoding="utf-8",
        )


@contextmanager
def kernel_process(root, selection, environment, *, digest=None):
    socket = root / "kernel.sock"
    instance = "a" * 64
    command = [sys.executable, "-B", "-m", "KERNEL_MIXER_C59.kernel_process",
               "--socket", str(socket), "--project-root", str(root),
               "--control-root", selection.control_relative.as_posix(), "--instance-id", instance,
               "--manifest-sha256", digest or selection.manifest_sha256,
               "--default-workbench-storage", "memory"]
    with (root / "kernel.log").open("w+") as log:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=log,
                                   env={**os.environ, **environment})
        try:
            with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(socket)),
                               base_url="http://private", timeout=5, trust_env=False) as client:
                yield process, client, instance, log
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=10)


def wait_ready(process, client, log, socket):
    deadline = time.monotonic() + 45
    while process.poll() is None and time.monotonic() < deadline:
        try:
            if socket.exists() and client.get("/health").status_code == 200:
                return
        except httpx2.TransportError:
            pass
        time.sleep(.05)
    log.seek(0)
    raise AssertionError(f"Kernel did not start: {log.read()}")
