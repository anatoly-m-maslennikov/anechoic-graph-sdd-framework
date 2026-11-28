"""Build and inspect the release canary container."""

from hashlib import sha256
import os
import re
from pathlib import Path
import subprocess

from ._release_canary_support import CanaryError
from .release_image__shared import IMAGE_DEADLINES, image_deadline_mode


def _container_command(
    project: Path, cidfile: Path, image: str, selection: dict
):
    instance_id = sha256(
        f"{project.resolve(strict=True)}\0{selection['control_root']}".encode(
            "utf-8"
        )
    ).hexdigest()
    command = [
        "docker",
        "run",
        "-d",
        "--pull=never",
        "--cidfile",
        str(cidfile),
    ]
    command += ["--init", "--read-only", "--cap-drop", "ALL"]
    command += ["--security-opt", "no-new-privileges:true"]
    command += ["--tmpfs", "/tmp:size=128m,mode=1777", "--pids-limit", "128"]
    command += ["--memory", "1536m", "--cpus", "1", "-p", "127.0.0.1::8092"]
    command += ["--mount", f"type=bind,src={project},dst=/project"]
    command += ["--mount", "type=volume,dst=/var/lib/anechoic"]
    command += ["-e", "ANECHOIC_FRAMEWORK_DB_ROOT=/var/lib/anechoic"]
    command += ["-e", "ANECHOIC_RUNTIME_NAMESPACE=docker"]
    command += ["-e", f"{IMAGE_DEADLINES}={image_deadline_mode(os.environ)}"]
    command += ["-e", f"ANECHOIC_CONTROL_ROOT={selection['control_root']}"]
    command += ["-e", f"ANECHOIC_PROJECT_INSTANCE_ID={instance_id}"]
    command += [
        "-e",
        f"ANECHOIC_HOST_PROJECT_ROOT={project}",
        image,
        "mcp-http",
    ]
    return command


def _inspect_canary(root: Path, container: str, timeout: float | None) -> str:
    return subprocess.run(
        [
            "docker",
            "container",
            "inspect",
            "--format",
            "{{.State.Running}}",
            container,
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    ).stdout.strip()


def _initialize_project(root: Path, project: Path, timeout: float | None):
    subprocess.run(
        ["git", "init", "--quiet", str(project)],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _published_port(root: Path, container: str, timeout: float | None) -> int:
    publisher = subprocess.run(
        ["docker", "port", container, "8092/tcp"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    ).stdout.strip()
    binding = re.fullmatch(r"127\.0\.0\.1:([1-9][0-9]{0,4})", publisher)
    if binding is None or int(binding[1]) > 65535:
        raise CanaryError("local-release-canary-port-invalid")
    return int(binding[1])
