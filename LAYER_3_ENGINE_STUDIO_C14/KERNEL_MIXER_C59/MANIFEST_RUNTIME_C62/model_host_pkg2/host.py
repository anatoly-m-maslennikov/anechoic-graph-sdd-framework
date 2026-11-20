"""Admit one compiled Model generation for the lifetime of this process."""

import hashlib
import json
from pathlib import Path
import re
import sys


def verify_model(generation: Path, expected_model_sha256: str) -> None:
    generation = Path(generation)
    descriptor = json.loads((generation / "model.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[0-9a-f]{64}", expected_model_sha256) or descriptor.get("model_sha256") != expected_model_sha256:
        raise ValueError("model hash mismatch")
    modules = descriptor.get("modules")
    if not isinstance(modules, dict) or "__init__.py" not in modules:
        raise ValueError("invalid model modules")
    package = generation / "anechoic_runtime_model"
    if {path.name for path in package.glob("*.py")} != set(modules):
        raise ValueError("model module set mismatch")
    for name, digest in modules.items():
        if not isinstance(name, str) or not name.endswith(".py") or not name[:-3].isidentifier():
            raise ValueError("invalid model module name")
        path = package / name
        if path.is_symlink() or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid model module")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != digest or (name == "__init__.py" and content):
            raise ValueError("model module hash mismatch")


def main() -> None:
    verify_model(Path(sys.argv[1]), sys.argv[2])
    print("ready", flush=True)
    for _ in sys.stdin.buffer:
        pass


if __name__ == "__main__":
    main()
