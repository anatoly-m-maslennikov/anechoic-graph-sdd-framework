"""Install the ANECHOIC hook and MCP connection in the user's Codex home."""

from __future__ import annotations

import ipaddress
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import tomllib
from urllib.parse import urlsplit


HOOK_SOURCE = Path("LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_CODEX_HOOK/codex_hook.py")
MATCHER = "^mcp__anechoic__.*$"


def _regular_path(path: Path, *, directory: bool = False) -> None:
    if path.is_symlink() or (path.exists() and not (path.is_dir() if directory else path.is_file())):
        raise ValueError(f"Unsafe or conflicting path: {path}")


def _atomic_write(path: Path, data: bytes) -> bool:
    _regular_path(path)
    if path.exists() and path.read_bytes() == data:
        return False
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def _validate_endpoint(endpoint: str) -> None:
    try:
        parsed = urlsplit(endpoint)
        host = parsed.hostname
        loopback = host == "localhost" or (host is not None and ipaddress.ip_address(host).is_loopback)
        if (parsed.scheme != "http" or not loopback or parsed.port is None or
                parsed.username is not None or parsed.password is not None or
                parsed.query or parsed.fragment):
            raise ValueError
    except ValueError:
        raise ValueError("Codex MCP endpoint must be an HTTP loopback URL with a port") from None


def _configured_server(config_path: Path, hook_path: Path) -> dict | None:
    _regular_path(config_path)
    if not config_path.exists():
        return None
    with config_path.open("rb") as handle:
        config = tomllib.load(handle)
    if json.dumps(str(hook_path))[1:-1] in json.dumps(config.get("hooks", {}), default=str):
        raise ValueError("Conflicting inline Codex hook registration")
    servers = config.get("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ValueError("Invalid Codex MCP server configuration")
    server = servers.get("anechoic")
    if server is not None and not isinstance(server, dict):
        raise ValueError("Conflicting Codex anechoic MCP configuration")
    return server


def install_codex(source_root: Path, endpoint: str, *, codex_home: Path | None = None,
                  executor=subprocess.run) -> dict:
    """Install on explicit request; the caller must ensure the endpoint is ready."""
    _validate_endpoint(endpoint)
    source = Path(source_root) / HOOK_SOURCE
    _regular_path(source)
    hook_data = source.read_bytes()
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is required to run the Python 3.14 Codex hook")
    home = Path(codex_home or os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().absolute()
    _regular_path(home, directory=True)
    hook_dir = home / "anechoic"
    hook_path = hook_dir / "codex_hook.py"
    hooks_path = home / "hooks.json"
    config_path = home / "config.toml"
    _regular_path(hook_dir, directory=True)
    _regular_path(hook_path)
    _regular_path(hooks_path)
    if hook_path.exists() and hook_path.read_bytes() != hook_data:
        raise ValueError(f"Conflicting existing Codex hook: {hook_path}")
    server = _configured_server(config_path, hook_path)
    if server is not None and (server.get("url") != endpoint or server.get("enabled") is False or
                               any(key in server for key in ("command", "bearer_token_env_var", "http_headers", "env_http_headers"))):
        raise ValueError("Conflicting Codex anechoic MCP configuration")
    hooks_data, added_group = _hook_registration(hooks_path, hook_path, uv)
    home.mkdir(parents=True, exist_ok=True)
    hook_dir.mkdir(exist_ok=True)
    registered = False
    if server is None:
        _register_server(home, endpoint, config_path, hook_path, executor)
        registered = True
    hook_changed = _atomic_write(hook_path, hook_data)
    hooks_changed = _atomic_write(hooks_path, hooks_data) if added_group else False
    return {"hook_path": str(hook_path), "hooks_path": str(hooks_path), "endpoint": endpoint,
            "mcp_registered": registered, "hook_changed": hook_changed,
            "hooks_changed": hooks_changed, "approval": "Review and trust the hook in Codex /hooks."}


def _validate_hook_groups(groups: list, group: dict, hook_path: Path) -> None:
    for existing in groups:
        if not isinstance(existing, dict):
            raise ValueError("Invalid Codex PreToolUse group")
        if existing.get("matcher") == MATCHER and existing != group:
            raise ValueError("Conflicting existing ANECHOIC hook registration")
        handlers = existing.get("hooks", [])
        if not isinstance(handlers, list):
            raise ValueError("Invalid Codex PreToolUse handlers")
        for handler in handlers:
            if not isinstance(handler, dict):
                raise ValueError("Invalid Codex hook handler")
            if str(hook_path) in str(handler.get("command", "")) and existing != group:
                raise ValueError("Conflicting existing ANECHOIC hook registration")

def _hook_registration(hooks_path: Path, hook_path: Path, uv: str) -> tuple[bytes, bool]:
    document = json.loads(hooks_path.read_text(encoding="utf-8")) if hooks_path.exists() else {}
    if not isinstance(document, dict) or not isinstance(document.setdefault("hooks", {}), dict):
        raise ValueError("Invalid Codex hooks configuration")
    groups = document["hooks"].setdefault("PreToolUse", [])
    if not isinstance(groups, list):
        raise ValueError("Invalid Codex PreToolUse configuration")
    args = [uv, "run", "--no-project", "--no-env-file", "--managed-python", "--python", "3.14", str(hook_path)]
    command = subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)
    group = {"matcher": MATCHER, "hooks": [{"type": "command", "command": command}]}
    _validate_hook_groups(groups, group, hook_path)
    if groups.count(group) > 1:
        raise ValueError("Duplicate ANECHOIC hook registration")
    added_group = group not in groups
    if added_group:
        groups.append(group)
    hooks_data = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return hooks_data, added_group


def _register_server(home: Path, endpoint: str, config_path: Path, hook_path: Path, executor) -> None:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(home)
    executor(["codex", "mcp", "add", "anechoic", "--url", endpoint],
             cwd=home, env=env, check=True, capture_output=True, text=True, timeout=30)
    registered_server = _configured_server(config_path, hook_path)
    if registered_server is None or registered_server.get("url") != endpoint:
        raise RuntimeError("Codex did not register the requested MCP endpoint")
