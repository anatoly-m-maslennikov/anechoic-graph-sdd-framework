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
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    BoundNativeModel, is_reviewed_claim, normalize_reviewed_claim, validate_model_instance,
)
from .model_class_assembly import assemble_model_classes, model_module_name
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import model_class_target
from .model_declaration_sources import _check_relation_references, _merge_constraint_claims


_ASSETS = Path(__file__).resolve().parent.parent / "FEATURE_GENERATED_MODEL_C52"
_CLAIM_FILES = {
    "native-graph-claims.json": "69700992be5b44bf0280676e9def93edb1fd2181cb25777d0e7dd7a8816b3ba5",
    "native-spec-template-claims.json": "c07981a1e918c478edbf21032270ead06e0d8c6cb769f42700bd245307747cdd",
}

_OLD_ATOM = "Node//Artifact//Atom"
_NEW_ATOM = "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
_OLD_SEED_TARGET = _OLD_ATOM + "//Spec Atom//Component Seed Manifest"
_SEED_SUBJECT = "MODEL//ANECHOIC <+ " + _OLD_SEED_TARGET
_CHECK_TARGET_MIGRATION = {
    _OLD_ATOM: _NEW_ATOM,
    **{_OLD_ATOM + "//Spec Atom" + suffix: _NEW_ATOM + "//Specification" + suffix
       for suffix in ("//Manifest//Project Manifest", "//Manifest//Component Manifest",
                      "//Purpose", "//Contract")},
    _OLD_SEED_TARGET:
        _NEW_ATOM + "//Specification//Manifest//Component Seed Manifest",
}


def _previous_seed_claim(claim):
    return claim.replace(
        "    purpose: str | None = None\n    contract: str | None = None\n    solution: str | None = None\n",
        "    purpose: str\n    solution: str\n",
    ).replace("and spec.component_seed_id[2:].isdigit())",
              "and spec.component_seed_id[2:].isdigit() and spec.purpose.strip() and spec.solution.strip())")


def reviewed_model_records():
    """Return normalized reviewed Claims, their originals, and a source fingerprint."""
    records, originals = [], {}
    digest = sha256(b"retire-component-purpose\0component-manifest-tiers-1-and-4\0")
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
                claim = claim.replace(old, 'tier: int = field(metadata={"allowed_values": (1, 4)})')
            records.append((name, subject, normalize_reviewed_claim(claim)))
    _check_relation_references(records)
    return records, originals, digest.hexdigest()


def admit_active_model_records(records):
    """Validate Active declarations and keep executable checks pinned."""
    reviewed, originals, _ = reviewed_model_records()
    checks, targets = {}, {}
    for _, subject, claim in reviewed:
        declaration = parse_native_model_claim(claim)
        if check := declaration.get("instance_check"):
            target = model_class_target(subject, declaration["arguments"]["entity_name"])
            checks[target] = (check["name"], check["parameter_type"], check["source"])
            targets[target] = target
            if target in _CHECK_TARGET_MIGRATION:
                targets[_CHECK_TARGET_MIGRATION[target]] = target
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
        check = declaration.get("instance_check")
        args = declaration["arguments"]
        target = model_class_target(subject, args.get("entity_name")) if "entity_class" in args else None
        original_target = targets.get(target)
        expected = checks.get(original_target)
        actual = (check["name"], check["parameter_type"], check["source"]) if check else None
        if actual != expected and original_target == _OLD_SEED_TARGET:
            previous = _previous_seed_claim(originals[_SEED_SUBJECT])
            previous_check = parse_native_model_claim(normalize_reviewed_claim(previous))["instance_check"]
            expected = (previous_check["name"], previous_check["parameter_type"], previous_check["source"])
            if actual == expected:
                originals[_SEED_SUBJECT] = previous
        if actual != expected or (check and (args.get("entity_class") != check["parameter_type"]
                                              or original_target in seen)):
            raise ValueError(f"{source}: executable Model instance check differs from the approved review")
        if check:
            seen.add(original_target)
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
            original = next((value for value in originals.values()
                             if is_reviewed_claim(name, value)), None)
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
