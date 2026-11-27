"""Check the installed Test Suite prerequisites without preparing them."""

import json
import os
from pathlib import Path
import subprocess
import sys

from .full_suite_docker import IMAGE_DEADLINES
from .functional_suite import WORKBENCH
from .suite_config import load_suite_config


FRONTEND = WORKBENCH / "FEATURE_IWE_CONSOLE_FRONTEND"
CHROMIUM_PROBE = FRONTEND / "FEATURE_IWE_CONSOLE_FRONTEND__tests/pinned_chromium_probe.ts"
WORKBENCH_CACHE = Path(".anechoic_tmp/workbench")
DUCKPGQ_VERSION = "9c11bc192a"


def _run(command, frontend, *, env=None) -> str:
    result = subprocess.run(command, cwd=frontend, env=env, text=True,
                            capture_output=True, check=False, timeout=45)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or
                         f"{command[0]} exited with status {result.returncode}")
    return result.stdout.strip()


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _check_frontend(frontend: Path) -> str:
    manifest = _read_json(frontend / "package.json")
    lock = _read_json(frontend / "package-lock.json")["packages"]
    for group in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        declared = manifest.get(group, {})
        if declared != lock[""].get(group, {}):
            raise ValueError(f"{group} differ between package.json and package-lock.json")
        for name in declared:
            if f"node_modules/{name}" not in lock:
                raise ValueError(f"package-lock.json does not pin {name}")
    for location, locked in lock.items():
        if not location:
            continue
        if not location.startswith("node_modules/") or ".." in Path(location).parts:
            raise ValueError(f"invalid package lock path: {location}")
        installed = frontend / location / "package.json"
        if locked.get("optional") and not installed.exists():
            continue
        observed = _read_json(installed)["version"]
        if observed != locked["version"]:
            raise ValueError(f"{location} is {observed}; package-lock.json pins {locked['version']}")
    _run(("npm", "ls", "--all", "--include=dev", "--offline", "--ignore-scripts",
          "--no-update-notifier", "--logs-max=0"), frontend)
    _run(("node", "--input-type=module", "-e",
          'import "rollup"; import { transformSync } from "esbuild"; transformSync("0");'), frontend)
    return "Locked Workbench frontend dependencies are ready"


def _check_duckpgq(root: Path, extensions: Path) -> str:
    import duckdb

    runtime = load_suite_config(root)["dependency-groups"]["runtime"]
    pins = [requirement.removeprefix("duckdb==") for requirement in runtime
            if requirement.startswith("duckdb==")]
    if len(pins) != 1 or duckdb.__version__ != pins[0]:
        raise ValueError(f"DuckDB {duckdb.__version__} does not match the engine pin ({', '.join(pins)})")
    with duckdb.connect(":memory:", config={
        "extension_directory": str(extensions),
        "autoinstall_known_extensions": False,
        "autoload_known_extensions": False,
    }) as connection:
        connection.execute("LOAD duckpgq")
        connection.execute("SET active_grammar_extensions = ['duckpgq']")
        loaded = connection.execute(
            "SELECT extension_version FROM duckdb_extensions() WHERE extension_name = 'duckpgq' AND loaded"
        ).fetchone()
        if loaded != (DUCKPGQ_VERSION,):
            observed = loaded[0] if loaded else "unknown"
            raise ValueError(f"Loaded DuckPGQ {observed}; expected {DUCKPGQ_VERSION}")
    return f"DuckPGQ {DUCKPGQ_VERSION} loaded in DuckDB {duckdb.__version__} from {extensions}"


def _check_chromium(frontend: Path, probe: Path, browsers: Path) -> str:
    environment = {**os.environ, IMAGE_DEADLINES: "1", "PLAYWRIGHT_BROWSERS_PATH": str(browsers)}
    version = _run(("node", str(probe)),
                   frontend, env=environment)
    return f"Pinned Chromium {version} launched from {browsers}"


def run_preflight(root: Path, report: dict) -> int:
    frontend = root / FRONTEND
    browsers = root / WORKBENCH_CACHE / "playwright-browsers"
    extensions = root / Path(os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", WORKBENCH_CACHE / "extensions"))
    checks = (
        (_check_frontend, (frontend,), f"Locked frontend dependencies unavailable. Run `npm ci` in {frontend}"),
        (_check_duckpgq, (root, extensions), f"Pinned DuckPGQ unavailable in {extensions}"),
        (_check_chromium, (frontend, root / CHROMIUM_PROBE, browsers), f"Pinned Chromium could not launch from {browsers}"),
    )
    report["step"] = "preflight"
    failures = []
    for check, arguments, remedy in checks:
        try:
            print(check(*arguments), flush=True)
        except Exception as error:
            message = f"{remedy}. {error}"
            failures.append(message)
            print(f"Preflight failed: {message}", file=sys.stderr, flush=True)
    if failures:
        report["error"] = "\n".join(failures)
    return int(bool(failures))
