"""Compare versioned carrier checkpoints by folder and path."""
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re


def folder_hashes(hashes):
    if not isinstance(hashes, dict):
        raise ValueError("Invalid carrier checkpoint")
    folders = {}
    for name, digest in hashes.items():
        if not isinstance(name, str) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Invalid carrier checkpoint")
        path = PurePosixPath(name)
        if path.is_absolute() or path.as_posix() != name or ".." in path.parts or "\\" in name or not path.name:
            raise ValueError("Invalid carrier checkpoint path")
        folders.setdefault(path.parent.as_posix(), []).append((path.name, digest))
    return {folder: sha256(json.dumps(sorted(rows), ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
            for folder, rows in folders.items()}


def changed_paths(previous, current):
    folders = folder_hashes(previous)
    new_folders = folder_hashes(current)
    changed = {folder for folder in folders.keys() | new_folders.keys() if folders.get(folder) != new_folders.get(folder)}
    return sorted(path for path in previous.keys() | current.keys()
                  if PurePosixPath(path).parent.as_posix() in changed and previous.get(path) != current.get(path))
