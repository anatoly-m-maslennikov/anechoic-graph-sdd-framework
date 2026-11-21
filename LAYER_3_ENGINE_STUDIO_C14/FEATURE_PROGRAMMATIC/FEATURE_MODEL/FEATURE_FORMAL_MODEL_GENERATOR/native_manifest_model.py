"""Load the ANECHOIC Model and bind its reviewed executable checks."""

from functools import lru_cache
from importlib import import_module
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType
from uuid import uuid4

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.reviewed_instance_check import bind_reviewed_instance_check
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.validate_model_instance import validate_model_instance
from .model_class_assembly import assemble_model_classes, model_module_name
from model_class_subject import model_class_target
from .model_declaration_sources import _check_relation_references, _merge_constraint_claims, _relation_registry


_ASSETS = Path(__file__).resolve().parent.parent / "FEATURE_GENERATED_MODEL"
_CLAIM_FILES = {
    "native-graph-claims.json": "777f959c571424e73503cde96c78065d9da3cb1b04eb312cb8976f4b8faf60eb",
    "native-spec-template-claims.json": "1d847774691f91b37db6445ce892810d8fe47e86f9d87b960d951dc2a3da437a",
}
_REVIEWED_CHECKS = {
    "check_atom_identity": "1756b0e117c6b68ae719f52cb805a69d2a2d198feb9a2996b94869698e13cd09",
    "check_project_manifest": "771c1c72eeae6ea67e1658e647fc3062dc07f725506372ff284d181b3cfe9b39",
    "check_component_manifest": "47532369ca1bc4cbd73611f09a27b6142aafb453e1eb156b10198bc4d98dc978",
    "check_purpose": "a080c8a08f9b2f066992045de8183f532eb0aa6fb1dc566e746bc3bed2701a3b",
    "check_contract": "087afdc97f4a8add78336871fbf1f3698718b97200fad1518f96ef8c20a72007",
    "check_package_spec": "8fb0a7cb026469fd2d3a020be0f9eb852dd4fc16b4c4610fa4131f39b24e698b",
}


def _native_imports(claim):
    # The approved bytes predate the Engine package rename.
    claim = claim.replace("from caprmedio.formal_claims import ", "from anechoic.formal_claims import ")
    return claim.replace("from caprmedio.model import ", "from anechoic.model import ")


def reviewed_model_records():
    """Return normalized reviewed Claims, their originals, and a source fingerprint."""
    records, originals = [], {}
    digest = sha256(b"retire-component-purpose\0")
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
            records.append((name, row["subject"], _native_imports(claim)))
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


class _NativeModel:
    def __init__(self, compiled=False, records=None):
        records, originals, self.fingerprint = (
            reviewed_model_records() if records is None else admit_active_model_records(records)
        )
        parsed = _merge_constraint_claims(
            [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records]
        )
        self.requires_atom_state = any(declaration["arguments"].get("derived_from_properties")
                                       for _, _, declaration in parsed)
        module = None
        if compiled:
            model_types = {
                name: getattr(import_module(f"anechoic_runtime_model.{model_module_name(name)}"), name)
                for _, _, declaration in parsed
                if (name := declaration["arguments"].get("entity_class"))
            }
        else:
            module = ModuleType(f"_reviewed_anechoic_native_model_{uuid4().hex}")
            sys.modules[module.__name__] = module
        try:
            if module is not None:
                exec(assemble_model_classes(claim for _, _, claim in records), vars(module))
                model_types = vars(module)
            self._bindings, self._types, self._population = bind_model_declarations(
                [(subject, declaration) for _, subject, declaration in parsed], model_types,
            )
            self._endpoints = _relation_registry(parsed)
            self._checks = {}
            for _, subject, declaration in parsed:
                if check := declaration.get("instance_check"):
                    name = check["name"]
                    original_subject = next(key for key, value in originals.items()
                                            if sha256(value.encode()).hexdigest() == _REVIEWED_CHECKS[name])
                    if sha256(originals[original_subject].encode()).hexdigest() != _REVIEWED_CHECKS[name]:
                        raise ValueError(f"{subject}: Claim differs from reviewed source")
                    claim = _native_imports(originals[original_subject])
                    self._checks[check["parameter_type"]] = (name, bind_reviewed_instance_check(
                        claim, reference=subject, reviewed_claim_sha256=sha256(claim.encode()).hexdigest(),
                        model_types=model_types,
                    ))
        except BaseException:
            if module is not None:
                del sys.modules[module.__name__]
            raise
        self.relation_types = frozenset(self._endpoints)
        self._parent_relation = "IS_CHILD_OF" if "IS_CHILD_OF" in self.relation_types else "CHILD_OF"
        self.relation_classifications = {
            name: args.get("inverse_classifications" if reverse else "classifications", {}).copy()
            for name, (args, reverse) in self._endpoints.items()
        }
        self.requires_atom_header = "atom_family" in self._types["Atom"].__dataclass_fields__
        self.inverses = {name: args["inverse_alias"] for name, (args, reverse) in self._endpoints.items()
                         if not reverse and "inverse_alias" in args}

    def _validate(self, name, properties, relations):
        model_class = self._types[name]
        has_supplied_ref = "ref_id" in properties and isinstance(getattr(model_class, "ref_id", None), property)
        if has_supplied_ref:
            supplied_ref = properties["ref_id"]
            properties = {key: value for key, value in properties.items() if key != "ref_id"}
        instance = validate_model_instance(
            model_class, properties=properties, outgoing_relations=relations,
            relation_declarations=self._bindings, model_types=self._types,
            checks=dict(self._checks[base.__name__] for base in model_class.__mro__
                        if base.__name__ in self._checks),
            population_declarations=self._population, population_peers={self._types["Atom"]: ()},
            endpoint_registry=self._endpoints,
        )
        if has_supplied_ref and supplied_ref != instance.ref_id:
            raise ValueError("ref_id: supplied value differs from derived Ref ID")
        return instance

    def validate_manifest(self, fields, component_id):
        if component_id != "C00":
            raise ValueError("Project Manifest must be contained by Project C00")
        project = self._validate("Project", {}, {})
        return self._validate("Project Manifest", fields, {"CONTAINED_BY": [project]})

    def validate_component_manifest(self, fields, parent_id):
        project = self._validate("Project", {}, {})
        parent = project if parent_id == "C00" else self._validate("Component", {}, {self._parent_relation: [project]})
        self._validate("Component", {}, {self._parent_relation: [parent]})
        return self._validate("Component Manifest", fields, {"CONTAINED_BY": [parent]})

    def validate_package_spec(self, fields, owner_id):
        project = self._validate("Project", {}, {})
        owner = project if owner_id == "C00" else self._validate("Component", {}, {self._parent_relation: [project]})
        return self._validate("Package Spec", fields, {"CONTAINED_BY": [owner]})


def load_compiled_model(records=None):
    """Bind reviewed declarations to the compiler-generated runtime classes."""
    return _NativeModel(compiled=True, records=records)


@lru_cache(maxsize=1)
def load_native_model():
    """Load only the pinned, reviewed Model and its checks."""
    return _NativeModel()
