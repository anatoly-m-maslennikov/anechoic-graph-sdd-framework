"""Create the native Manifest for an explicitly requested new Project."""

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import secrets


_RESERVED = {"new", "legacy", "legacy_archive", "runtime", "tmp", "install", "archive"}


def initialize_project(source_checkout: Path, project: Path, name: str, prefix: str, *,
                       workbench_storage: str, journal_storage: str) -> Path:
    """Create a Project control root; refuse existing Projects and unsafe paths."""
    source = Path(source_checkout)
    model = source / "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_GENERATED_MODEL_C52"
    if not all((model / filename).is_file() for filename in
               ("native-graph-claims.json", "native-spec-template-claims.json")):
        raise ValueError("Source checkout does not contain the reviewed native Model")
    raw = Path(project).expanduser()
    if (".." in raw.parts or any(part == ".env" or part.startswith(".env.") or part.endswith(".env")
                                 or part in {".ssh", ".aws", ".gnupg"} for part in raw.parts)):
        raise ValueError("Project path must not contain '..'")
    root = Path(os.path.abspath(raw))
    if not root.is_dir() or root.resolve(strict=True) != root:
        raise ValueError("Project root must be an existing directory without symlinks")
    if (not isinstance(name, str) or not name or name != name.strip() or not name[0].isalnum()
            or any(not (c.isalnum() or c in " _.-") for c in name)
            or name.casefold() in _RESERVED or len(name.casefold().encode()) > 200):
        raise ValueError("Project name cannot form a safe native control root")
    if not isinstance(prefix, str) or re.fullmatch(r"[A-Z]+", prefix) is None or len(prefix) > 64:
        raise ValueError("Project prefix must contain uppercase ASCII letters")
    if workbench_storage not in {"disk", "memory"} or journal_storage not in {"files", "duckdb"}:
        raise ValueError("Invalid Project storage mode")
    control = root / (".anechoic_" + name.casefold())
    atom_id = f"{prefix}-S-1"
    manifest = root / f"{atom_id}-SPEC-PROJECT_MANIFEST--declare-project.md"
    body = _manifest_body(atom_id, name, prefix, workbench_storage, journal_storage)
    _write_manifest(root, control.name, manifest.name, body)
    return control


def _manifest_body(atom_id: str, name: str, prefix: str, workbench_storage: str, journal_storage: str) -> str:
    updated = datetime.now(timezone.utc).isoformat()
    return (f"---\natom_family: SPEC\natom_id: {atom_id}\ncontainer:\n  component: C00\n"
            f"tier: -1\ncontext:\n  template: project_manifest\n  lens: SPEC\n"
            f"state:\n  status: active\n  version: 1\n  updated_at: '{updated}'\n---\n\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n\n"
            "declare_entity(\n"
            "    entity_name='Project Manifest',\n"
            "    instance=ProjectManifest(\n"
            f"        name={name!r},\n"
            f"        prefix={prefix!r},\n"
            "        parameters={\n"
            "            'runtime': {\n"
            f"                'workbench': {{'storage': {workbench_storage!r}}},\n"
            f"                'journal': {{'storage': {journal_storage!r}}},\n"
            "            },\n"
            "        },\n"
            "    ),\n"
            ")\n```\n")


def _write_manifest(root: Path, control: str, manifest: str, body: str) -> None:
    root_fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in root.parts[1:]:
            child_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
            os.close(root_fd)
            root_fd = child_fd
        with os.scandir(root_fd) as entries:
            for entry in entries:
                match = re.fullmatch(r"[._]anechoic_(.+)", entry.name)
                if match and match.group(1) not in _RESERVED:
                    raise FileExistsError(f"Project control candidate already exists: {entry.name}")
                if re.fullmatch(r".+-PROJECT_MANIFEST--.+\.md", entry.name):
                    raise FileExistsError(f"Project Manifest already exists: {entry.name}")
        os.mkdir(control, dir_fd=root_fd)
        control_stat = os.stat(control, dir_fd=root_fd, follow_symlinks=False)
        try:
            _publish_manifest(root_fd, manifest, body)
        except BaseException:
            try:
                current = os.stat(control, dir_fd=root_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == (control_stat.st_dev, control_stat.st_ino):
                    os.rmdir(control, dir_fd=root_fd)
            except OSError:
                pass
            raise
    finally:
        os.close(root_fd)


def _publish_manifest(control_fd: int, manifest: str, body: str) -> None:
    temporary = ".project-manifest-" + secrets.token_hex(16) + ".tmp"
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o666, dir_fd=control_fd)
    owned = os.fstat(fd)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, manifest, src_dir_fd=control_fd, dst_dir_fd=control_fd,
                follow_symlinks=False)
    finally:
        try:
            current = os.stat(temporary, dir_fd=control_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) == (owned.st_dev, owned.st_ino):
                os.unlink(temporary, dir_fd=control_fd)
        except FileNotFoundError:
            pass
