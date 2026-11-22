"""Persist Beta Workspace and View state for one Project."""

from hashlib import sha256
import json
import os
from pathlib import Path
import stat
from uuid import uuid4, uuid7
from fcntl import flock, LOCK_EX


_DIRECTORY = (".anechoic_runtime", "workbench", "beta", "workspaces")
_DIRECTORY_FLAGS = os.O_DIRECTORY | os.O_NOFOLLOW | os.O_RDONLY
_WORKSPACE = {"workspace_id"}
_VIEW = _WORKSPACE | {"view_id"}
_ARGUMENTS = {
    "workspace_open": ({"session_id"}, set()),
    "workspace_list": (set(), set()),
    "workspace_get": (_WORKSPACE, set()),
    "view_create": (_WORKSPACE, {"name", "position"}),
    "view_duplicate": (_VIEW, set()),
    "view_list": (_WORKSPACE, set()),
    "view_get": (_VIEW, set()),
    "view_update": (_VIEW | {"sql", "expected_revision"}, {"cursor_position"}),
    "view_focus": (_VIEW, set()),
    "view_rename": (_VIEW | {"name"}, set()),
    "view_remove": (_VIEW, set()),
}


def _text(value, field, *, nonempty=False):
    if not isinstance(value, str) or (nonempty and not value.strip()):
        kind = "a non-empty string" if nonempty else "a string"
        raise ValueError(f"{field} must be {kind}")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise ValueError(f"{field} must be valid UTF-8") from error
    return value


def _nonnegative(value, field):
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _filename(workspace_id):
    return f"{sha256(workspace_id.encode()).hexdigest()}.json"


def _read_document(directory, filename):
    fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    with os.fdopen(fd, encoding="utf-8") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise ValueError("workspace is unavailable")
        return json.load(stream)


def _write_document(directory, document):
    filename = _filename(document["workspace_id"])
    temporary = f".{uuid4().hex}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temporary, flags, 0o600, dir_fd=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, ensure_ascii=False, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, filename, src_dir_fd=directory, dst_dir_fd=directory)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


def _new_view():
    return {"id": str(uuid7()), "sql": "", "cursor_position": 0, "revision": 0}


def _view_list(document):
    return {
        "workspace_id": document["workspace_id"],
        "active_view_id": document["active_view_id"],
        "views": [{key: value for key, value in view.items() if key != "sql"} for view in document["views"]],
    }


def _view_response(document, view):
    return {"workspace_id": document["workspace_id"], "view_id": view["id"]} | view


def _duplicate(views, source):
    names = [view.get("name") or f"View {index + 1}" for index, view in enumerate(views)]
    index = views.index(source)
    base_name = names[index]
    suffix = 1
    while f"{base_name}({suffix})" in names:
        suffix += 1
    view = _new_view() | {
        "sql": source["sql"], "cursor_position": source["cursor_position"], "name": f"{base_name}({suffix})",
    }
    views.insert(index + 1, view)
    return view


class WorkspaceStore:
    def __init__(self, root: Path):
        self._root = root.resolve(strict=True)

    def _open_directory(self, create):
        fd = os.open(self._root, _DIRECTORY_FLAGS)
        try:
            for part in _DIRECTORY:
                if create:
                    try:
                        os.mkdir(part, mode=0o700, dir_fd=fd)
                    except FileExistsError:
                        pass
                child = os.open(part, _DIRECTORY_FLAGS, dir_fd=fd)
                os.close(fd)
                fd = child
                info = os.fstat(fd)
                if info.st_uid != os.getuid() or info.st_mode & 0o022:
                    raise ValueError("workspace directory is unavailable or unsafe")
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _read(self, directory, filename):
        try:
            document = _read_document(directory, filename)
            workspace_id = _text(document["workspace_id"], "workspace_id", nonempty=True)
            views = document["views"]
            if (set(document) != {"workspace_id", "project_root", "active_view_id", "views"}
                    or filename != _filename(workspace_id) or document["project_root"] != str(self._root)
                    or not isinstance(views, list) or not views):
                raise ValueError("invalid workspace document")
            ids = set()
            for view in views:
                required = {"id", "sql", "cursor_position", "revision"}
                if set(view) not in (required, required | {"name"}):
                    raise ValueError("invalid workspace view")
                ids.add(_text(view["id"], "view_id", nonempty=True))
                _text(view["sql"], "sql")
                if "name" in view:
                    _text(view["name"], "name", nonempty=True)
                _nonnegative(view["cursor_position"], "cursor_position")
                _nonnegative(view["revision"], "revision")
            if len(ids) != len(views) or document["active_view_id"] not in ids:
                raise ValueError("invalid workspace view binding")
            return document
        except FileNotFoundError:
            raise
        except (OSError, KeyError, TypeError, ValueError) as error:
            raise ValueError("workspace is unavailable") from error

    def _list(self, directory):
        ids = []
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                try:
                    ids.append(self._read(directory, filename)["workspace_id"])
                except (FileNotFoundError, ValueError):
                    continue
        return {"items": [{"workspace_id": value} for value in sorted(ids)]}

    def invoke(self, operation: str, arguments: dict) -> dict:
        """Apply one explicit state operation under the Project's store lock."""
        if not isinstance(operation, str) or operation not in _ARGUMENTS:
            raise ValueError("unknown Workbench interface operation")
        required, optional = _ARGUMENTS[operation]
        if not isinstance(arguments, dict) or not required <= arguments.keys() <= required | optional:
            raise ValueError(f"invalid {operation} arguments")
        opening = operation == "workspace_open"
        id_field = "session_id" if opening else "workspace_id"
        if operation != "workspace_list":
            workspace_id = _text(arguments[id_field], id_field, nonempty=True)
        try:
            directory = self._open_directory(opening)
        except FileNotFoundError as error:
            if operation == "workspace_list":
                return {"items": []}
            raise ValueError("unknown workspace_id") from error
        except OSError as error:
            raise ValueError("workspace directory is unavailable or unsafe") from error
        try:
            flock(directory, LOCK_EX)
            if operation == "workspace_list":
                return self._list(directory)
            try:
                document = self._read(directory, _filename(workspace_id))
            except FileNotFoundError as error:
                if not opening:
                    raise ValueError("unknown workspace_id") from error
                view = _new_view()
                document = {"workspace_id": workspace_id, "project_root": str(self._root),
                            "active_view_id": view["id"], "views": [view]}
                _write_document(directory, document)
            if document["workspace_id"] != workspace_id:
                raise ValueError("workspace is unavailable")
            if operation in ("workspace_open", "workspace_get"):
                return document
            if operation == "view_list":
                return _view_list(document)
            return self._view_operation(operation, arguments, directory, document)
        except OSError as error:
            raise ValueError("workspace is unavailable") from error
        finally:
            os.close(directory)

    def _view_operation(self, operation, arguments, directory, document):
        views = document["views"]
        if operation == "view_create":
            position = arguments.get("position", "last")
            if position not in ("first", "last"):
                raise ValueError("position must be first or last")
            view = _new_view()
            name = arguments.get("name")
            if name is not None and _text(name, "name").strip():
                view["name"] = name
            views.insert(0 if position == "first" else len(views), view)
        else:
            if operation == "view_remove" and len(views) == 1:
                raise ValueError("cannot remove the last view")
            view_id = _text(arguments["view_id"], "view_id", nonempty=True)
            view = next((view for view in views if view["id"] == view_id), None)
            if view is None:
                raise ValueError("unknown view_id")
            if operation == "view_get":
                return _view_response(document, view)
            if operation == "view_duplicate":
                view = _duplicate(views, view)
            elif operation == "view_remove":
                views.remove(view)
                if document["active_view_id"] == view["id"]:
                    document["active_view_id"] = views[0]["id"]
            elif operation == "view_update":
                self._update(view, arguments)
            elif operation == "view_rename":
                name = _text(arguments["name"], "name")
                if name.strip():
                    view["name"] = name
                else:
                    view.pop("name", None)
        if operation in ("view_create", "view_duplicate", "view_focus"):
            document["active_view_id"] = view["id"]
        _write_document(directory, document)
        if operation in ("view_create", "view_duplicate"):
            return document | {"view_id": view["id"]}
        if operation == "view_remove":
            return _view_list(document)
        if operation == "view_focus":
            return {"workspace_id": document["workspace_id"], "active_view_id": view["id"]}
        return _view_response(document, view)

    @staticmethod
    def _update(view, arguments):
        if "cursor_position" in arguments:
            view["cursor_position"] = _nonnegative(arguments["cursor_position"], "cursor_position")
        sql = _text(arguments["sql"], "sql")
        expected = _nonnegative(arguments["expected_revision"], "expected_revision")
        if view["revision"] != expected:
            raise ValueError("expected_revision does not match")
        view["sql"] = sql
        view["revision"] += 1
