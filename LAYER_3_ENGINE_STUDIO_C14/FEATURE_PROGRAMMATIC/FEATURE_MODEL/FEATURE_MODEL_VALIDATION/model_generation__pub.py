"""Verify and bind an attested compiled Model generation."""

from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from types import ModuleType
from uuid import uuid4


def _verified_generation(generation, expected_model_sha256, descriptor_sha256):
    generation = Path(generation)
    raw = (generation / "model.json").read_bytes()
    if descriptor_sha256 is not None and sha256(raw).hexdigest() != descriptor_sha256:
        raise ValueError("model descriptor hash mismatch")
    descriptor = json.loads(raw)
    if not re.fullmatch(r"[0-9a-f]{64}", expected_model_sha256) or descriptor.get("model_sha256") != expected_model_sha256:
        raise ValueError("model hash mismatch")
    modules = descriptor.get("modules")
    if not isinstance(modules, dict) or "__init__.py" not in modules:
        raise ValueError("invalid model modules")
    package = generation / "anechoic_runtime_model"
    if {path.name for path in package.glob("*.py")} != set(modules):
        raise ValueError("model module set mismatch")
    verified = {}
    for name, digest in modules.items():
        if not isinstance(name, str) or not name.endswith(".py") or not name[:-3].isidentifier():
            raise ValueError("invalid model module name")
        path = package / name
        if path.is_symlink() or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid model module")
        content = path.read_bytes()
        if sha256(content).hexdigest() != digest or (name == "__init__.py" and content):
            raise ValueError("model module hash mismatch")
        verified[name] = content
    return descriptor, verified


def verify_model(generation: Path, expected_model_sha256: str, *, descriptor_sha256=None) -> None:
    _verified_generation(generation, expected_model_sha256, descriptor_sha256)


@contextmanager
def open_admitted_model(generation: Path, fingerprint: str, descriptor_sha256: str):
    """Bind one attested generation from the same bytes that passed verification."""
    from .bound_native_model import BoundNativeModel

    if not isinstance(descriptor_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", descriptor_sha256):
        raise ValueError("missing Model descriptor attestation")
    descriptor, modules = _verified_generation(generation, fingerprint, descriptor_sha256)
    order = descriptor["module_order"]
    if (descriptor.get("binding_schema") != 1 or not isinstance(order, list)
            or len(order) != len(modules) - 1 or set(order) != modules.keys() - {"__init__.py"}):
        raise ValueError("invalid runtime Model module order or binding schema")
    package = ModuleType(f"_anechoic_model_{uuid4().hex}")
    package.__path__ = []
    loaded = {}
    sys.modules[package.__name__] = package
    try:
        for filename in order:
            name = Path(filename).stem
            module = ModuleType(f"{package.__name__}.{name}")
            module.__package__ = package.__name__
            sys.modules[module.__name__] = loaded[name] = module
            setattr(package, name, module)
            exec(compile(modules[filename], str(generation / "anechoic_runtime_model" / filename), "exec"),
                 vars(module))
        classes = {name: getattr(loaded[module], name) for name, module in descriptor["class_modules"].items()}
        yield BoundNativeModel(descriptor["bindings"], classes, fingerprint)
    finally:
        for module in loaded.values():
            sys.modules.pop(module.__name__, None)
        sys.modules.pop(package.__name__, None)


