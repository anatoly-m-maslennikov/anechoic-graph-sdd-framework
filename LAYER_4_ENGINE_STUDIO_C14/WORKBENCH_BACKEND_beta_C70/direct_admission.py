"""Refuse requests against a direct Project whose Manifest binding is stale."""

import json
import os
from pathlib import Path

from .peer_transport import tool_failure


def direct_admission():
    binding = os.environ.get("ANECHOIC_BETA_DIRECT_MANIFEST")
    if binding is None:
        return lambda: None
    value = json.loads(binding)
    manifest, gate = Path(value["path"]), Path(value["gate"])
    expected = tuple(value["version"])

    def failure():
        try:
            if gate.read_text(encoding="ascii") == "project_manifest_invalid":
                return tool_failure("project_manifest_invalid", "The Project Manifest is invalid")
        except FileNotFoundError:
            try:
                info = manifest.lstat()
                version = (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
                if version == expected:
                    return None
            except OSError:
                pass
        except (OSError, UnicodeError):
            pass
        return tool_failure("project_manifest_reloading", "The Project Manifest binding is being reloaded")

    return failure
