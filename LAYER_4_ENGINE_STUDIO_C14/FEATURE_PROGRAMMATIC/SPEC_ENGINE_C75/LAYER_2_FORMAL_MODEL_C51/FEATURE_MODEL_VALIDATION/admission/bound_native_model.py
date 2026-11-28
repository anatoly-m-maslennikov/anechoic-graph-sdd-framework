"""Bind admitted Model declarations to generated runtime classes."""

from hashlib import sha256
from types import SimpleNamespace as SimpleNamespace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_content,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    status_domains,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.model.cardinality__pub import (
    cardinality_bounds,
)
from ._project_spec_validation import (
    project_spec_template as _project_spec_template,
    validate_project_spec as _validate_project_spec,
)
from ._reviewed_claim_hashes import _PRIOR_SEED_CHECK, _REVIEWED_CHECKS
from ..model_declaration_bindings import bind_model_declarations
from ..model_relation_validation import effective_relation_constraints
from .reviewed_instance_check import bind_reviewed_instance_check
from ..validate_model_instance import validate_model_instance


def is_reviewed_claim(name: str, claim: str) -> bool:
    digest = sha256(claim.encode()).hexdigest()
    return digest == _REVIEWED_CHECKS.get(name) or (
        name == "check_component_seed_manifest" and digest == _PRIOR_SEED_CHECK
    )


def normalize_reviewed_claim(claim: str) -> str:
    claim = claim.replace(
        "from caprmedio.formal_claims import ",
        "from anechoic.formal_claims import ",
    )
    return claim.replace(
        "from caprmedio.model import ", "from anechoic.model import "
    )


def _project_spec_summary_fields(body):
    summaries = [
        section["direct_markdown"]
        for section in parse_content(body, tolerate_duplicate_siblings=True)
        if section["property_path"] == ["summary"]
    ]
    if len(summaries) > 1:
        raise ValueError("Project SPEC has duplicate Summary properties")
    return (
        {"summary": summaries[0].strip()}
        if summaries and summaries[0] is not None
        else {}
    )


class BoundNativeModel:
    """Bind an admitted, serializable Model to its generated classes."""

    def __init__(self, bindings, model_types, fingerprint):
        self.fingerprint = fingerprint
        self.status_domains = status_domains(bindings)
        declarations = bindings["declarations"]
        self.requires_atom_state = any(
            declaration["arguments"].get("derived_from_properties")
            for _, declaration in declarations
        )
        self._bindings, self._types, self._population = (
            bind_model_declarations(declarations, model_types)
        )
        self._declared_types = [
            (
                subject,
                d["arguments"]["entity_name"],
                model_types[d["arguments"]["entity_class"]],
                d["arguments"].get("creation_enabled", True),
            )
            for subject, d in declarations
            if "entity_class" in d["arguments"]
        ]
        self._endpoints = {
            name: (args, reverse)
            for name, (args, reverse) in bindings["endpoints"].items()
        }
        self._bind_instance_checks(bindings, declarations, model_types)
        self._bind_relations()

    def _bind_instance_checks(self, bindings, declarations, model_types):
        expected = _expected_checks(declarations)
        self._checks = {}
        seen = set()
        for parameter_type, name, subject, original in bindings["checks"]:
            if name in seen or not is_reviewed_claim(name, original):
                raise ValueError(
                    f"{subject}: Claim differs from reviewed source"
                )
            claim = normalize_reviewed_claim(original)
            check = parse_native_model_claim(claim).get("instance_check")
            if (
                name not in expected
                or expected[name][0] != subject
                or check["source"] != expected[name][1]["source"]
                or check["name"] != name
                or check["parameter_type"] != parameter_type
                or expected[name][1]["parameter_type"] != parameter_type
                or parameter_type in self._checks
            ):
                raise ValueError(
                    f"{subject}: executable Model instance check differs "
                    "from the approved review"
                )
            self._checks[parameter_type] = (
                name,
                bind_reviewed_instance_check(
                    claim,
                    reference=subject,
                    reviewed_claim_sha256=sha256(claim.encode()).hexdigest(),
                    model_types=model_types,
                ),
            )
            seen.add(name)
        if seen != set(expected) or seen != set(_REVIEWED_CHECKS):
            raise ValueError(
                "Active Model is missing reviewed instance checks"
            )

    def _bind_relations(self):
        self.relation_types = frozenset(self._endpoints)
        self._parent_relation = (
            "IS_CHILD_OF"
            if "IS_CHILD_OF" in self.relation_types
            else "CHILD_OF"
        )
        self._containment_relation = (
            "IS_CONTAINED_BY"
            if "IS_CONTAINED_BY" in self.relation_types
            else "CONTAINED_BY"
        )
        self.relation_axes = {
            name: args.get("inverse_axes" if reverse else "axes", {}).copy()
            for name, (args, reverse) in self._endpoints.items()
        }
        self.requires_atom_header = (
            "atom_family" in self._types["Atom"].__dataclass_fields__
        )
        self.inverses = {
            name: args["inverse_alias"]
            for name, (args, reverse) in self._endpoints.items()
            if not reverse and "inverse_alias" in args
        }

    def _validate_instance(self, *args, **kwargs):
        return validate_model_instance(*args, **kwargs)

    def _validate(self, name, properties, relations):
        model_class = self._types[name]
        has_supplied_ref = "ref_id" in properties and isinstance(
            getattr(model_class, "ref_id", None), property
        )
        if has_supplied_ref:
            supplied_ref = properties["ref_id"]
            properties = {
                key: value
                for key, value in properties.items()
                if key != "ref_id"
            }
        instance = self._validate_instance(
            model_class,
            properties=properties,
            outgoing_relations=relations,
            relation_declarations=self._bindings,
            model_types=self._types,
            checks=dict(
                self._checks[base.__name__]
                for base in model_class.__mro__
                if base.__name__ in self._checks
            ),
            population_declarations=self._population,
            population_peers={self._types["Atom"]: ()},
            endpoint_registry=self._endpoints,
        )
        if has_supplied_ref and supplied_ref != instance.ref_id:
            raise ValueError(
                "ref_id: supplied value differs from derived Ref ID"
            )
        return instance

    @property
    def ticket_labels(self):
        ticket = self._types.get("Ticket Atom")
        label = getattr(ticket, "__dataclass_fields__", {}).get("label")
        return (
            tuple(label.metadata.get("allowed_values", ()))
            if label is not None
            else ()
        )

    def declares_summary(self, name):
        return self.declares_property(name, "summary")

    def declares_property(self, name, property_name):
        return property_name in self._types[name].__dataclass_fields__

    def fixed_property_value(self, name, property_name):
        field = self._types[name].__dataclass_fields__.get(property_name)
        metadata = field.metadata if field is not None else {}
        allowed = metadata.get("allowed_values", ())
        cardinality = metadata.get("value_cardinality")
        if (
            len(allowed) == 1
            and cardinality is not None
            and cardinality_bounds(cardinality) == (1, 1)
        ):
            return allowed[0]
        return None

    def validate_manifest(self, fields, component_id):
        if component_id != "C00":
            raise ValueError(
                "Project Manifest must be contained by Project C00"
            )
        project = self._validate("Project", {}, {})
        return self._validate(
            "Project Manifest", fields, {self._containment_relation: [project]}
        )

    def validate_component_manifest(self, fields, parent_id):
        project = self._validate("Project", {}, {})
        parent = (
            project
            if parent_id == "C00"
            else self._validate(
                "Component", {}, {self._parent_relation: [project]}
            )
        )
        self._validate("Component", {}, {self._parent_relation: [parent]})
        return self._validate(
            "Component Manifest",
            fields,
            {self._containment_relation: [parent]},
        )

    def project_spec_template(self, template):
        return _project_spec_template(
            self, template, effective_relation_constraints
        )

    def validate_project_spec(self, template, header, owner_id, body=None):
        return _validate_project_spec(
            self,
            template,
            header,
            owner_id,
            body,
            _project_spec_summary_fields,
        )

    def validate_component_seed_manifest(self, fields, owner_id):
        project = self._validate("Project", {}, {})
        owner = (
            project
            if owner_id == "C00"
            else self._validate(
                "Component", {}, {self._parent_relation: [project]}
            )
        )
        return self._validate(
            "Component Seed Manifest",
            fields,
            {self._containment_relation: [owner]},
        )


def _expected_checks(declarations):
    expected = {}
    for subject, declaration in declarations:
        if check := declaration.get("instance_check"):
            name = check["name"]
            if name in expected:
                raise ValueError(f"{subject}: duplicate Model instance check")
            expected[name] = (subject, check)
    return expected
