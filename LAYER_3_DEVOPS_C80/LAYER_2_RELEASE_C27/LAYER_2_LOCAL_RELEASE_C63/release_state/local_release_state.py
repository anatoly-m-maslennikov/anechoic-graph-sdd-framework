"""Persist Local Release evidence before and after each phase."""

import json
import os
import stat
import sys
import tomllib as tomllib
from datetime import datetime as datetime
from datetime import timezone as timezone
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile

from .local_release_journal import Journal as Journal
from .local_release_journal import (
    _legacy_gate_evidence as _legacy_gate_evidence,
)
from .local_release_journal import release_evidence as release_evidence

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    _LAYER_NAMES,
    LocalReleaseError,
    _file_identity,
    _project_path,
    _walk_regular_files,
)

_RUNS = Path(".anechoic_runtime/simple_local_release/runs")
_STAGES = Path(".anechoic_tmp/simple_local_release")
_OWNED = (*map(Path, _LAYER_NAMES), Path(".agents/skills/ane"))
_EXCLUDED = frozenset(
    {
        ".git",
        ".anechoic_runtime",
        ".anechoic_tmp",
        ".anechoic_install",
        "000_anechoic_framework",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        ".vite",
    }
)
PHASES = (
    "validate inputs",
    "bump candidate version",
    "static tests",
    "functional tests",
    "copy active sources",
    "build package",
    "prepare candidate image",
    "verify candidate image",
    "verify candidate canary",
    "copy product to installed framework",
    "install project runtime",
    "start mcp",
    "final",
)
_OLD_PHASES = tuple(
    phase for phase in PHASES if phase != "verify candidate canary"
)


def abort_request_path(root, journal_path):
    return _project_path(
        root,
        journal_path.parent.relative_to(root) / "abort-requested",
        label="release-abort",
    )


def failure_evidence(journal, error, port):
    data = journal.data if journal is not None else {}
    phases = PHASES[1:2] + PHASES[4:7] + PHASES[9:12]
    if data.get("source_binding") is not None:
        phases = tuple(
            phase
            for phase in phases
            if phase not in {"bump candidate version", "copy active sources"}
        )
    done = data.get("done", ())
    effects = [{"phase": phase} for phase in phases if phase in done]
    if data.get("source_binding") is None and data.get("head") is not None:
        effects.insert(0, {"phase": "git checkpoint", "head": data["head"]})
    if (
        "bump candidate version" not in done
        and journal is not None
        and data.get("version") is not None
        and _version_applied(journal, data["version"][1])
    ):
        effects.append({"phase": "bump candidate version"})
    result = {"effects": effects}
    if "evidence" in data:
        result["evidence"] = data["evidence"]
    if port is not None:
        result["port"] = port
    notes = _startup_diagnostics(error)
    if notes:
        result["diagnostics"] = notes
    return result


def _startup_diagnostics(error):
    return [
        note[:4096]
        for note in getattr(error, "__notes__", ())
        if note.startswith("Local Release startup diagnostics: ")
    ][:2]


def _version_applied(journal, expected):
    try:
        path = _project_path(
            journal.root,
            Path("version.toml"),
            label="version-path",
            require_exists=True,
        )
        return path.read_text(encoding="utf-8") == expected
    except LocalReleaseError, OSError, UnicodeError:
        return False


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w", dir=path.parent, encoding="utf-8", delete=False
    ) as output:
        temporary = Path(output.name)
        try:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
            if path.is_file():
                temporary.chmod(path.stat().st_mode & 0o777)
            os.replace(temporary, path)
            descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        finally:
            temporary.unlink(missing_ok=True)


def _read(path):
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, encoding="utf-8") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                raise ValueError("invalid journal file")
            raw = source.read(32 * 1024 * 1024 + 1)
        if len(raw) > 32 * 1024 * 1024:
            raise ValueError("oversized journal")
        return json.loads(raw)
    except (OSError, ValueError) as error:
        raise LocalReleaseError(
            "local-release-resume-journal-invalid"
        ) from error


def _checked(data, run_id):
    if (
        not isinstance(data, dict)
        or data.get("schema") not in (1, 2)
        or data.get("run_id") != run_id
        or not isinstance(data.get("done"), list)
        or (
            data.get("working") is not None
            and data.get("working") not in PHASES
        )
        or not isinstance(data.get("binding"), list)
        or not isinstance(data.get("options"), list)
        or len(data["options"]) != 2
        or not isinstance(data.get("logs"), dict)
        or not isinstance(data.get("proofs", {}), dict)
        or (
            "docker_context" in data
            and data["docker_context"] is not None
            and not isinstance(data["docker_context"], str)
        )
        or not _checked_failures(data.get("failures", []))
        or (
            data.get("result") is not None
            and not isinstance(data["result"], dict)
        )
    ):
        raise LocalReleaseError("local-release-resume-journal-invalid")
    done = data["done"]
    expected = (
        list(_OLD_PHASES[: len(done)])
        if data["schema"] == 1
        else [phase for phase in PHASES if phase in done]
    )
    if done != expected or (data.get("working") in done):
        raise LocalReleaseError("local-release-resume-journal-invalid")
    if data["schema"] == 1:
        _upgrade_combined_gate(data)
    if data.get("delivery") is not None and any(
        phase not in done for phase in PHASES[:9]
    ):
        raise LocalReleaseError("local-release-resume-journal-invalid")
    return data


def _checked_failures(failures):
    return isinstance(failures, list) and all(
        isinstance(item, dict) and isinstance(item.get("logs"), dict)
        for item in failures
    )


def _upgrade_combined_gate(data):
    data.update(schema=2, legacy_inputs=data.pop("inputs", None), proofs={})
    if "verify candidate image" in data["done"]:
        if not isinstance(data.get("canary"), str):
            raise LocalReleaseError("local-release-resume-journal-invalid")
        data["done"].insert(
            PHASES.index("verify candidate canary"), "verify candidate canary"
        )
    source = data.get("source_binding")
    build = data.get("provenance", {}).get("head_commit")
    data.update(
        accepted_source_sha=source[1] if source else build or data.get("head"),
        build_source_sha=build,
    )


def binding(selection):
    return [
        str(selection.root),
        selection.instance_id,
        selection.control_relative.as_posix(),
        selection.manifest_path.relative_to(selection.root).as_posix(),
        selection.manifest_ref,
    ]


def _same_source_binding(recorded, selected):
    if recorded is None or selected is None:
        return recorded == selected
    return (
        isinstance(recorded, list)
        and len(recorded) == len(selected)
        and (recorded[:1] + recorded[2:] == selected[:1] + selected[2:])
    )


def _delivery_record(root):
    path = _project_path(
        root, _RUNS.with_name("delivery.json"), label="resume-delivery"
    )
    value = _read(path) if path.exists() else {}
    if value != {} and (
        not isinstance(value, dict)
        or set(value) != {"run_id"}
        or not isinstance(value["run_id"], str)
    ):
        raise LocalReleaseError("local-release-resume-delivery-invalid")
    return path, value


def _current_delivery(data, latest):
    prior = data.get("delivery")
    origin = prior if prior is not None else data.get("delivery_seen")
    return latest in (origin, {"run_id": data["run_id"]})


def open_artifacts(root):
    """Yield staging paths, image IDs, and logs for open Local Releases."""
    directory = _project_path(root, _RUNS, label="resume-journal")
    if not directory.exists():
        return
    _, latest = _delivery_record(root)
    for entry in directory.iterdir():
        path = _project_path(
            root, _RUNS / entry.name / "state.json", label="resume-journal"
        )
        if not path.is_file():
            continue
        data = _checked(_read(path), entry.name)
        if (data.get("result") or {}).get(
            "outcome"
        ) != "completed" and _current_delivery(data, latest):
            logs = tuple(data["logs"].values()) + tuple(
                path
                for failure in data.get("failures", ())
                for path in failure["logs"].values()
            )
            yield data.get("staging"), data.get("image_id"), logs


def source_identity(root, runner_root, *, external=True):
    digest = sha256()
    _hash_tree(digest, root)
    if external and runner_root != root:
        _hash_tree(digest, runner_root)
    digest.update(json.dumps(test_environment()).encode())
    return digest.hexdigest()


def test_environment():
    image_fanout = os.environ.get("ANECHOIC_TEST_IMAGE_FANOUT")
    return (
        sys.platform,
        os.uname().machine,
        sys.version,
        os.environ.get("PATH"),
        os.environ.get("DOCKER_HOST"),
        os.environ.get("DOCKER_CONTEXT"),
        os.environ.get("ANECHOIC_TEST_IMAGE_DEADLINES"),
        os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY"),
        os.environ.get("ANECHOIC_TEST_FANOUT"),
        os.environ.get("PLAYWRIGHT_BROWSERS_PATH"),
        *((image_fanout,) if image_fanout is not None else ()),
    )


def _hash_tree(digest, root):
    digest.update(str(root).encode())
    files = _walk_regular_files(
        root,
        excluded_directories=_EXCLUDED,
        excluded_root_directories=frozenset(
            name.casefold() for name in _LAYER_NAMES
        ),
    )
    for path in files:
        relative = path.relative_to(root)
        if any(relative.is_relative_to(owned) for owned in _OWNED):
            continue
        encoded = json.dumps(
            (relative.as_posix(), _file_identity(path)), ensure_ascii=True
        )
        digest.update(encoded.encode())
