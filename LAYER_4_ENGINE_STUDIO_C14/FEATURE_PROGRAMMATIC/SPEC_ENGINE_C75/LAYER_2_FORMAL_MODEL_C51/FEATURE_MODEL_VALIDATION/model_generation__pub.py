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
    if (
        descriptor_sha256 is not None
        and sha256(raw).hexdigest() != descriptor_sha256
    ):
        raise ValueError("model descriptor hash mismatch")
    descriptor = json.loads(raw)
    if (
        not re.fullmatch(r"[0-9a-f]{64}", expected_model_sha256)
        or descriptor.get("model_sha256") != expected_model_sha256
    ):
        raise ValueError("model hash mismatch")
    modules = descriptor.get("modules")
    if not isinstance(modules, dict) or "__init__.py" not in modules:
        raise ValueError("invalid model modules")
    package = generation / "anechoic_runtime_model"
    if {path.name for path in package.glob("*.py")} != set(modules):
        raise ValueError("model module set mismatch")
    verified = {}
    for name, digest in modules.items():
        if (
            not isinstance(name, str)
            or not name.endswith(".py")
            or not name[:-3].isidentifier()
        ):
            raise ValueError("invalid model module name")
        path = package / name
        if (
            path.is_symlink()
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            raise ValueError("invalid model module")
        content = path.read_bytes()
        if sha256(content).hexdigest() != digest or (
            name == "__init__.py" and content
        ):
            raise ValueError("model module hash mismatch")
        verified[name] = content
    return descriptor, verified


def verify_model(
    generation: Path, expected_model_sha256: str, *, descriptor_sha256=None
) -> None:
    _verified_generation(generation, expected_model_sha256, descriptor_sha256)


def _validate_binding_descriptor(descriptor, modules):
    if not isinstance(descriptor, dict):
        raise ValueError("invalid Model descriptor")
    fingerprint = descriptor.get("model_sha256")
    order = descriptor.get("module_order")
    classes = descriptor.get("class_modules")
    if (
        not isinstance(fingerprint, str)
        or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
        or descriptor.get("binding_schema") != 1
        or not isinstance(order, list)
        or any(not isinstance(item, str) for item in order)
        or len(order) != len(modules) - 1
        or set(order) != modules.keys() - {"__init__.py"}
        or not isinstance(classes, dict)
        or any(
            not isinstance(name, str)
            or not name.isidentifier()
            or not isinstance(module, str)
            or module not in {Path(item).stem for item in order}
            for name, module in classes.items()
        )
        or not isinstance(descriptor.get("bindings"), dict)
    ):
        raise ValueError("invalid runtime Model binding descriptor")
    return fingerprint, order, classes


@contextmanager
def _bind_model(descriptor, modules, source_label):
    from .bound_native_model import BoundNativeModel

    fingerprint, order, classes = _validate_binding_descriptor(
        descriptor, modules
    )
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
            exec(
                compile(
                    modules[filename], f"{source_label}/{filename}", "exec"
                ),
                vars(module),
            )
        model_types = {
            name: getattr(loaded[module], name)
            for name, module in classes.items()
        }
        yield BoundNativeModel(
            descriptor["bindings"], model_types, fingerprint
        )
    finally:
        for module in loaded.values():
            sys.modules.pop(module.__name__, None)
        sys.modules.pop(package.__name__, None)


@contextmanager
def open_admitted_model(
    generation: Path, fingerprint: str, descriptor_sha256: str
):
    """Bind one attested generation from the same bytes that passed \
verification."""
    if not isinstance(descriptor_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", descriptor_sha256
    ):
        raise ValueError("missing Model descriptor attestation")
    descriptor, modules = _verified_generation(
        generation, fingerprint, descriptor_sha256
    )
    with _bind_model(
        descriptor, modules, str(generation / "anechoic_runtime_model")
    ) as model:
        yield model


@contextmanager
def open_serialized_model(descriptor):
    "Bind the exact module sources in an already admitted Model descriptor."
    if not isinstance(descriptor, dict):
        raise ValueError("invalid Model descriptor")
    hashes, sources = (
        descriptor.get("modules"),
        descriptor.get("module_sources"),
    )
    if (
        not isinstance(hashes, dict)
        or not isinstance(sources, dict)
        or "__init__.py" not in hashes
        or set(sources) != set(hashes)
    ):
        raise ValueError("invalid serialized Model module set")
    modules = {}
    for name, digest in hashes.items():
        source = sources[name]
        if (
            not isinstance(name, str)
            or not name.endswith(".py")
            or not name[:-3].isidentifier()
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not isinstance(source, str)
        ):
            raise ValueError("invalid serialized Model module")
        content = source.encode("utf-8")
        if sha256(content).hexdigest() != digest or (
            name == "__init__.py" and content
        ):
            raise ValueError("serialized Model module hash mismatch")
        modules[name] = content
    with _bind_model(descriptor, modules, "<admitted-model>") as model:
        yield model
