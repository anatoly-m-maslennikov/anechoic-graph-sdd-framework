"""Read the Release fields of one native Project Manifest without executing its claim.

This is a narrow Release input contract, not validation against the compiled Model.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import re
import stat

from markdown_it import MarkdownIt
import yaml


_RESERVED = {prefix + name for prefix in (".anechoic_", "_anechoic_")
             for name in ("new", "legacy", "legacy_archive", "runtime", "tmp")}
_PROTECTED = {".ssh", ".aws", ".gnupg"}
_MAX_FILE = 64 * 1024 * 1024


@dataclass(frozen=True)
class ReleaseSelection:
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: Path
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, object]

    @property
    def launcher_state(self) -> Path:
        return self.root / ".anechoic_runtime/runtime/project_mcp" / self.instance_id


def _protected(path: Path) -> bool:
    return any(part in _PROTECTED or part == ".env" or part.startswith(".env.") or part.endswith(".env")
               for part in path.parts)


def _directory(path: Path) -> int:
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _version(info: os.stat_result) -> tuple[int, ...]:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _read(fd: int, name: str) -> tuple[bytes, tuple[int, ...]]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > _MAX_FILE:
            raise ValueError("Manifest source is not a bounded regular file")
        raw = stream.read(_MAX_FILE + 1)
        if len(raw) != before.st_size or _version(before) != _version(os.fstat(stream.fileno())):
            raise ValueError("Manifest source changed during read")
        return raw, _version(before)


def _names(fd: int, *, controls: bool) -> tuple[str, ...]:
    with os.scandir(fd) as entries:
        names = []
        for index, entry in enumerate(entries, 1):
            if index > 1_000_000:
                raise ValueError("Project inventory exceeds the host ceiling")
            if controls:
                if not entry.name.startswith((".anechoic_", "_anechoic_")) or entry.name in _RESERVED:
                    continue
                if entry.is_symlink():
                    raise ValueError("Project control candidates must not be symlinks")
                if entry.is_dir(follow_symlinks=False):
                    names.append(entry.name)
                    if len(names) > 64:
                        raise ValueError("Project control candidates exceed the host ceiling")
            elif entry.name.endswith(".md"):
                names.append(entry.name)
        return tuple(sorted(names))


def read_atom_header(text: str) -> tuple[dict, str]:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("Missing YAML frontmatter")
    front, body = text[4:].split("\n---\n", 1)
    depth = 0
    for count, event in enumerate(yaml.parse(front, Loader=yaml.SafeLoader), 1):
        if isinstance(event, yaml.events.AliasEvent):
            raise ValueError("YAML aliases are unsupported")
        if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
            depth += 1
        if isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
            depth -= 1
        if depth > 64 or count > 100_000:
            raise ValueError("YAML exceeds the parser safety ceiling")
    node = yaml.compose(front, Loader=yaml.SafeLoader)
    pending = [node]
    while pending:
        current = pending.pop()
        if isinstance(current, yaml.MappingNode):
            keys = [key.value for key, _ in current.value
                    if isinstance(key, yaml.ScalarNode) and key.tag == "tag:yaml.org,2002:str"]
            if len(keys) != len(current.value) or len(set(keys)) != len(keys):
                raise ValueError("YAML keys must be unique strings")
            pending.extend(child for pair in current.value for child in pair)
        elif isinstance(current, yaml.SequenceNode):
            pending.extend(current.value)
    metadata = yaml.safe_load(front)
    if not isinstance(metadata, dict):
        raise ValueError("Atom header must be a mapping")
    return metadata, body


def _literal(node: ast.AST):
    for item in ast.walk(node):
        if isinstance(item, ast.Dict):
            keys = [ast.literal_eval(key) if key is not None else None for key in item.keys]
            if any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
                raise ValueError("Claim mapping keys must be unique strings")
    return ast.literal_eval(node)


def _claim(body: str) -> dict:
    headings, claims = [], []
    tokens = MarkdownIt("commonmark").parse(body)
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [item for item in headings if item[0] < level]
            headings.append((level, tokens[index + 1].content.strip().casefold()))
        elif (token.type == "fence" and token.info.strip().casefold() == "python"
              and tuple(name for _, name in headings) == ("claim", "formal claim")):
            claims.append(token.content)
    if len(claims) != 1:
        raise ValueError("Expected one Python Formal Claim")
    tree = ast.parse(claims[0])
    imports = (("anechoic.formal_claims", "declare_entity"), ("anechoic.model", "ProjectManifest"))
    statements = tree.body
    if len(statements) != 3 or any(
        not isinstance(stmt, ast.ImportFrom) or stmt.level or stmt.module != module
        or len(stmt.names) != 1 or stmt.names[0].name != name or stmt.names[0].asname is not None
        for stmt, (module, name) in zip(statements[:2], imports)
    ):
        raise ValueError("Unsupported Project Manifest claim")
    expression = statements[2]
    if not isinstance(expression, ast.Expr) or not isinstance(expression.value, ast.Call):
        raise ValueError("Unsupported Project Manifest declaration")
    call = expression.value
    if not isinstance(call.func, ast.Name) or call.func.id != "declare_entity" or call.args:
        raise ValueError("Unsupported Project Manifest declaration")
    args = {arg.arg: arg.value for arg in call.keywords}
    if len(args) != len(call.keywords) or set(args) != {"entity_name", "instance"}:
        raise ValueError("Unsupported Project Manifest declaration arguments")
    instance = args["instance"]
    if (_literal(args["entity_name"]) != "Project Manifest" or not isinstance(instance, ast.Call)
            or not isinstance(instance.func, ast.Name) or instance.func.id != "ProjectManifest" or instance.args):
        raise ValueError("Expected a ProjectManifest instance")
    fields = {arg.arg: _literal(arg.value) for arg in instance.keywords}
    if (len(fields) != len(instance.keywords) or not {"name", "prefix"} <= fields.keys()
            or fields.keys() - {"name", "prefix", "parameters", "lens_whitelist"}):
        raise ValueError("Unsupported ProjectManifest fields")
    return fields


def _manifest(metadata: dict, body: str, name: str, relative: Path, digest: str, root: Path) -> ReleaseSelection:
    context, state = metadata.get("context"), metadata.get("state")
    if not isinstance(context, dict) or not isinstance(state, dict):
        raise ValueError("Manifest context and state are required")
    flat = "atom_family" in metadata
    identity = metadata.get("atom_id") if flat else (metadata.get("identity") or {}).get("atom_id")
    container = metadata.get("container") if flat else context.get("container")
    tier = metadata.get("tier") if flat else context.get("tier")
    version = state.get("version")
    if (context.get("template") != "project_manifest" or state.get("status") != "active"
            or container != {"component": "C00"} or type(tier) is not int or tier != -1
            or type(version) is not int or version < 1 or not isinstance(identity, str)
            or re.fullmatch(r"[A-Z]+-S-[0-9]+", identity) is None
            or not name.startswith(identity + "-") or (flat and metadata.get("atom_family") != "SPEC")):
        raise ValueError("Invalid Active Project Manifest header")
    fields = _claim(body)
    project_name, prefix = fields["name"], fields["prefix"]
    parameters = fields.get("parameters", {})
    if (not isinstance(project_name, str) or not project_name.strip() or not isinstance(prefix, str)
            or re.fullmatch(r"[A-Z]+", prefix) is None or not identity.startswith(prefix + "-S-")
            or relative.name not in {f".anechoic_{project_name.casefold()}", f"_anechoic_{project_name.casefold()}"}
            or not isinstance(parameters, dict)):
        raise ValueError("Project Manifest identity contradicts the selected control root")
    project = parameters.get("project", {})
    project_root = project.get("root", {}) if isinstance(project, dict) else {}
    if isinstance(project_root, dict) and "prefix" in project_root:
        marker = {"dot": ".", "underscore": "_"}.get(project_root["prefix"])
        if marker is None or relative.name != f"{marker}anechoic_{project_name.casefold()}":
            raise ValueError("Project root prefix contradicts the selection")
    paths = parameters.get("paths", {})
    if isinstance(paths, dict) and "control_root" in paths and paths["control_root"] != relative.as_posix():
        raise ValueError("Project control_root contradicts the selection")
    instance = sha256(f"{root}\0{relative.as_posix()}".encode("utf-8")).hexdigest()
    return ReleaseSelection(root, root / relative, relative, instance, project_name, prefix,
                            root / relative / name, f"{identity}@{version}", digest, parameters)


def _scan_control(root_fd: int, control: str, root: Path, total_bytes: int):
    selection = None
    fd = os.open(control, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
    try:
        control_identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
        names = _names(fd, controls=False)
        records = []
        candidates = []
        has_manifest = False
        for name in names:
            raw, version = _read(fd, name)
            total_bytes += len(raw)
            if total_bytes > 1024 * 1024 * 1024:
                raise ValueError("Project inventory exceeds the read ceiling")
            digest = sha256(raw).hexdigest()
            records.append((name, version, digest))
            try:
                metadata, body = read_atom_header(raw.decode("utf-8"))
            except (ValueError, UnicodeError, yaml.YAMLError, RecursionError):
                if re.match(r"[A-Z]+-S-", name):
                    raise
                continue
            context = metadata.get("context")
            if isinstance(context, dict) and context.get("template") == "project_manifest":
                has_manifest = True
                if isinstance(metadata.get("state"), dict) and metadata["state"].get("status") == "active":
                    candidates.append(_manifest(metadata, body, name, Path(control), digest, root))
            elif "atom_family" not in metadata and "PROJECT_MANIFEST" in name:
                has_manifest = True
        if has_manifest:
            if len(candidates) != 1:
                raise ValueError("Expected one Active Project Manifest")
            selection = candidates[0]
        snapshot = (control, control_identity, names, records)
    finally:
        os.close(fd)
    return selection, snapshot, total_bytes


def _verify_snapshots(root_fd: int, snapshots, total_bytes: int) -> None:
    for control, identity, names, records in snapshots:
        fd = os.open(control, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
        try:
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) != identity or _names(fd, controls=False) != names:
                raise ValueError("Project control changed during selection")
            for name, version, digest in records:
                raw, current = _read(fd, name)
                total_bytes += len(raw)
                if total_bytes > 1024 * 1024 * 1024:
                    raise ValueError("Project inventory exceeds the read ceiling")
                if current != version or sha256(raw).hexdigest() != digest:
                    raise ValueError("Project carriers changed during selection")
            if _names(fd, controls=False) != names:
                raise ValueError("Project control changed during selection")
        finally:
            os.close(fd)


def _canonical_root(project_root: str | Path) -> Path:
    raw_root = Path(project_root).expanduser()
    if ".." in raw_root.parts or _protected(raw_root):
        raise ValueError("Project root is unsafe")
    root = Path(os.path.abspath(raw_root))
    if root == Path(root.anchor) or root.resolve(strict=True) != root:
        raise ValueError("Project root must be a non-symlink directory")
    return root


def read_release_selection(project_root: str | Path, control_relative: str | Path | None = None) -> ReleaseSelection:
    """Select one active native Project Manifest and pin the inputs read during selection."""
    try:
        root = _canonical_root(project_root)
        root_fd = _directory(root)
        try:
            root_identity = (os.fstat(root_fd).st_dev, os.fstat(root_fd).st_ino)
            if control_relative is None:
                controls = _names(root_fd, controls=True)
            else:
                relative = Path(control_relative)
                if (len(relative.parts) != 1 or str(control_relative) != relative.as_posix()
                        or not relative.name.startswith((".anechoic_", "_anechoic_"))
                        or relative.name in {".anechoic_", "_anechoic_"} or _protected(relative)):
                    raise ValueError("Control root must be a normalized direct Project child")
                controls = (relative.name,)
            selections = []
            snapshots = []
            total_bytes = 0
            for control in controls:
                selection, snapshot, total_bytes = _scan_control(root_fd, control, root, total_bytes)
                if selection is not None:
                    selections.append(selection)
                snapshots.append(snapshot)
            if len(selections) != 1:
                raise ValueError("A unique native Project Manifest is required")
            if control_relative is None and _names(root_fd, controls=True) != controls:
                raise ValueError("Project control candidates changed during selection")
            _verify_snapshots(root_fd, snapshots, total_bytes)
            if control_relative is None and _names(root_fd, controls=True) != controls:
                raise ValueError("Project control candidates changed during selection")
            current_root = _directory(root)
            try:
                info = os.fstat(current_root)
                if (info.st_dev, info.st_ino) != root_identity:
                    raise ValueError("Project root changed during selection")
            finally:
                os.close(current_root)
            return selections[0]
        finally:
            os.close(root_fd)
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError, yaml.YAMLError, RecursionError) as error:
        raise ValueError("Project Manifest is unavailable, invalid, or unsafe") from error
