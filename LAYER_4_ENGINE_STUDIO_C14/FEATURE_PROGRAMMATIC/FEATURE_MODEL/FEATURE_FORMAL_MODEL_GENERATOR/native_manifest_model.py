"""Load the ANECHOIC Model and bind its reviewed executable checks."""

from functools import lru_cache
from importlib import import_module
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType
from uuid import uuid4

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.relation_declaration_catalog__pub import build_relation_declaration_catalog
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    BoundNativeModel, normalize_reviewed_claim, reviewed_claim_sha256, validate_model_instance,
)
from .model_class_assembly import assemble_model_classes, model_module_name
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import model_class_target
from .model_declaration_sources import _check_relation_references, _merge_constraint_claims


_ASSETS = Path(__file__).resolve().parent.parent / "FEATURE_GENERATED_MODEL_C52"
_CLAIM_FILES = {
    "native-graph-claims.json": "69700992be5b44bf0280676e9def93edb1fd2181cb25777d0e7dd7a8816b3ba5",
    "native-spec-template-claims.json": "285840cd66c360787502c9fc1797b46c8eae447cb224bdf51a8c37534462ad10",
}

def reviewed_model_records():
    """Return normalized reviewed Claims, their originals, and a source fingerprint."""
    records, originals = [], {}
    digest = sha256(b"retire-component-purpose\0component-manifest-tier-4\0")
    for name, expected in _CLAIM_FILES.items():
        data = (_ASSETS / name).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"{name}: reviewed Claim file differs")
        digest.update(name.encode() + b"\0" + data)
        for row in json.loads(data):
            if row["subject"] == "MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Component Purpose":
                continue
            claim = row["claim"]
            originals[row["subject"]] = claim
            subject = row["subject"].replace("PMETA Atom", "Project Config Atom")
            claim = claim.replace("PMETA Atom", "Project Config Atom").replace("PMETAAtom", "ProjectConfigAtom")
            if subject.endswith("//Component Manifest"):
                old = 'tier: int = field(metadata={"allowed_values": (0,)})'
                if claim.count(old) != 1:
                    raise ValueError(f"{subject}: reviewed tier declaration differs")
                claim = claim.replace(old, 'tier: int = field(metadata={"allowed_values": (4,)})')
            records.append((name, subject, normalize_reviewed_claim(claim)))
    _check_relation_references(records)
    return records, originals, digest.hexdigest()


def admit_active_model_records(records):
    """Validate Active declarations and keep executable checks pinned."""
    reviewed, originals, _ = reviewed_model_records()
    checks = {}
    for _, subject, claim in reviewed:
        declaration = parse_native_model_claim(claim)
        if check := declaration.get("instance_check"):
            target = model_class_target(subject, declaration["arguments"]["entity_name"])
            checks[target] = check["source"]
    records = tuple(records)
    subjects = set()
    parsed = []
    for source, subject, claim in records:
        declaration = parse_native_model_claim(claim)
        if declaration is None or subject in subjects:
            raise ValueError(f"{source}: expected a unique Model Declaration")
        subjects.add(subject)
        parsed.append((source, subject, declaration))
    seen = set()
    for source, subject, declaration in _merge_constraint_claims(parsed):
        check = declaration.get("instance_check", {}).get("source")
        args = declaration["arguments"]
        target = model_class_target(subject, args.get("entity_name")) if "entity_class" in args else None
        if check != checks.get(target):
            raise ValueError(f"{source}: executable Model instance check differs from the approved review")
        if check:
            seen.add(target)
    if checks.keys() - seen:
        raise ValueError("Active Model is missing reviewed instance checks")
    _check_relation_references(records)
    fingerprint = sha256(json.dumps(sorted(records), ensure_ascii=False).encode()).hexdigest()
    return records, originals, fingerprint


def compile_native_bindings(records, originals):
    """Compile admitted declarations into serializable runtime bindings."""
    parsed = _merge_constraint_claims(
        [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records]
    )
    checks = []
    for _, subject, declaration in parsed:
        if check := declaration.get("instance_check"):
            name = check["name"]
            digest = reviewed_claim_sha256(name)
            original = next((value for value in originals.values()
                             if sha256(value.encode()).hexdigest() == digest), None)
            if original is None:
                raise ValueError(f"{subject}: Claim differs from reviewed source")
            checks.append([check["parameter_type"], name, subject, original])
    return {"declarations": [[subject, declaration] for _, subject, declaration in parsed],
            "endpoints": build_relation_declaration_catalog(parsed), "checks": checks}


class _NativeModel(BoundNativeModel):
    def _validate_instance(self, *args, **kwargs):
        return validate_model_instance(*args, **kwargs)

    def __init__(self, compiled=False, records=None):
        records, originals, fingerprint = (
            reviewed_model_records() if records is None else admit_active_model_records(records)
        )
        bindings = compile_native_bindings(records, originals)
        module = None
        if compiled:
            model_types = {
                name: getattr(import_module(f"anechoic_runtime_model.{model_module_name(name)}"), name)
                for _, declaration in bindings["declarations"]
                if (name := declaration["arguments"].get("entity_class"))
            }
        else:
            module = ModuleType(f"_reviewed_anechoic_native_model_{uuid4().hex}")
            sys.modules[module.__name__] = module
        try:
            if module is not None:
                exec(assemble_model_classes(claim for _, _, claim in records), vars(module))
                model_types = vars(module)
            super().__init__(bindings, model_types, fingerprint)
        except BaseException:
            if module is not None:
                del sys.modules[module.__name__]
            raise


def load_compiled_model(records=None):
    """Bind reviewed declarations to the compiler-generated runtime classes."""
    return _NativeModel(compiled=True, records=records)


@lru_cache(maxsize=1)
def load_native_model():
    """Load only the pinned, reviewed Model and its checks."""
    return _NativeModel()
