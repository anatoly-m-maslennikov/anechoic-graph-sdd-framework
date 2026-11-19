"""Load the reviewed ANECHOIC Model used to validate a native Manifest."""

from functools import lru_cache
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
from .model_class_assembly import assemble_model_classes
from .model_declaration_sources import _check_relation_references, _relation_registry


_ASSETS = Path(__file__).resolve().parent.parent / "FEATURE_GENERATED_MODEL"
_CLAIM_FILES = {
    "native-graph-claims.json": "777f959c571424e73503cde96c78065d9da3cb1b04eb312cb8976f4b8faf60eb",
    "native-spec-template-claims.json": "a5d5591aba56a21c73931d2eea54f9d17ed86c3e8c878c6b71c31394f1158f69",
}
_REVIEWED_CHECKS = {
    "check_atom_identity": "1756b0e117c6b68ae719f52cb805a69d2a2d198feb9a2996b94869698e13cd09",
    "check_project_manifest": "b68c693a62ef4e85fa2183582ffbc9b27d7e5391e7ca5c604e7be3a8d14d5c78",
    "check_component_manifest": "47532369ca1bc4cbd73611f09a27b6142aafb453e1eb156b10198bc4d98dc978",
    "check_purpose": "a080c8a08f9b2f066992045de8183f532eb0aa6fb1dc566e746bc3bed2701a3b",
    "check_component_purpose": "0e2405b84739f53ad22f70f2db415ab7576996b295592d2c63863abaab7a0e13",
    "check_contract": "087afdc97f4a8add78336871fbf1f3698718b97200fad1518f96ef8c20a72007",
    "check_package_spec": "8fb0a7cb026469fd2d3a020be0f9eb852dd4fc16b4c4610fa4131f39b24e698b",
}


class _NativeModel:
    def __init__(self):
        records, originals = [], {}
        for name, expected in _CLAIM_FILES.items():
            data = (_ASSETS / name).read_bytes()
            if sha256(data).hexdigest() != expected:
                raise ValueError(f"{name}: reviewed Claim file differs")
            for row in json.loads(data):
                claim = row["claim"]
                originals[row["subject"]] = claim
                # The approved bytes predate the Engine package rename.
                claim = claim.replace("from caprmedio.formal_claims import ", "from anechoic.formal_claims import ")
                claim = claim.replace("from caprmedio.model import ", "from anechoic.model import ")
                records.append((name, row["subject"], claim))
        _check_relation_references(records)
        module = ModuleType(f"_reviewed_anechoic_native_model_{uuid4().hex}")
        sys.modules[module.__name__] = module
        try:
            exec(assemble_model_classes(claim for _, _, claim in records), vars(module))
            parsed = [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records]
            self._bindings, self._types, self._population = bind_model_declarations(
                [(subject, declaration) for _, subject, declaration in parsed], vars(module),
            )
            self._endpoints = _relation_registry(parsed)
            self._checks = {}
            for (_, subject, claim), (_, _, declaration) in zip(records, parsed, strict=True):
                if check := declaration.get("instance_check"):
                    name = check["name"]
                    if sha256(originals[subject].encode()).hexdigest() != _REVIEWED_CHECKS[name]:
                        raise ValueError(f"{subject}: Claim differs from reviewed source")
                    # Bind the renamed Claim only after the approved original is verified.
                    self._checks[check["parameter_type"]] = (name, bind_reviewed_instance_check(
                        claim, reference=subject, reviewed_claim_sha256=sha256(claim.encode()).hexdigest(),
                        model_types=vars(module),
                    ))
        except BaseException:
            del sys.modules[module.__name__]
            raise
        self.relation_types = frozenset(self._endpoints)
        self.inverses = {name: args["inverse_alias"] for name, (args, reverse) in self._endpoints.items()
                         if not reverse and "inverse_alias" in args}

    def _validate(self, name, properties, relations):
        model_class = self._types[name]
        return validate_model_instance(
            model_class, properties=properties, outgoing_relations=relations,
            relation_declarations=self._bindings, model_types=self._types,
            checks=dict(self._checks[base.__name__] for base in model_class.__mro__
                        if base.__name__ in self._checks),
            population_declarations=self._population, population_peers={self._types["Atom"]: ()},
            endpoint_registry=self._endpoints,
        )

    def validate_manifest(self, fields, component_id):
        if component_id != "C00":
            raise ValueError("Project Manifest must be contained by Project C00")
        project = self._validate("Project", {}, {})
        return self._validate("Project Manifest", fields, {"CONTAINED_BY": [project]})


@lru_cache(maxsize=1)
def load_native_model():
    """Load only the pinned, reviewed Model and its checks."""
    return _NativeModel()
