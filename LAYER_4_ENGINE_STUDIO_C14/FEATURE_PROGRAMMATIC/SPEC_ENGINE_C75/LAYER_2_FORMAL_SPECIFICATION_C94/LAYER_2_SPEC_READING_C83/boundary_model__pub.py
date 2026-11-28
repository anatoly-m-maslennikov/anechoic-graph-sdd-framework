"""Bind a Component's formal Manifest, public Contract and Solution."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.components__shared import (
    component_contract_fences,
    parse_component_manifest,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    formal_claim_fences,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.carriers.content.atom_reference__pub import (
    derive_atom_ref,
)
from markdown_it import MarkdownIt

from ...LAYER_1_SOURCE_ADAPTERS_C95._package__shared import (
    SourceError,
    read_source,
)
from .boundary_sources__pub import recognized_claim, require_link


def load_boundary_model(
    root, component_id, manifest, contract=None, solution=None
):
    """Load exact pins, retain claims, and report unsupported input."""
    model_manifest = load_manifest(root, component_id, manifest)
    result = {"component_id": component_id, "manifest": model_manifest}
    solution, embedded, contract_carrier, issues = _load_contract(
        root, component_id, model_manifest, contract, solution, result
    )
    if solution is None:
        raise SourceError(
            "solution",
            solution,
            "source_pin",
            "solution: missing Solution source",
        )
    solution_carrier, result["solution"], solution_issues = _load_formal_claim(
        root, component_id, "solution", solution, 0 if embedded else 1
    )
    issues.extend(solution_issues)
    return _finish_boundary(
        result,
        issues,
        model_manifest,
        manifest,
        solution_carrier,
        contract_carrier,
        embedded,
    )


def _load_contract(
    root, component_id, model_manifest, contract, solution, result
):
    embedded = "contract" in model_manifest
    if not embedded and model_manifest["tier"] == 1:
        raise SourceError(
            "contract",
            model_manifest["source"],
            "claim",
            "manifest: missing Contract claim",
        )
    contract_carrier = None
    if embedded:
        if solution is None:
            solution = contract
        elif contract is not None:
            raise SourceError(
                "contract",
                contract,
                "source_pin",
                "Contract source is the pinned Manifest",
            )
        result.update(
            contract=model_manifest["contract"], embedded_contract=True
        )
        issues = list(model_manifest["contract_issues"])
    else:
        contract_carrier, result["contract"], issues = load_formal_claim(
            root, component_id, "contract", contract
        )
    return solution, embedded, contract_carrier, issues


def _finish_boundary(
    result,
    issues,
    model_manifest,
    manifest,
    solution_carrier,
    contract_carrier,
    embedded,
):
    target = result["contract"]["source"]
    if not embedded:
        require_link(
            contract_carrier,
            "ANSWERS",
            manifest["atom_id"],
            "contract",
            target,
        )
    target_ref = derive_atom_ref(
        target["atom_id"], target["version"], target["status"]
    )
    relation = "ANSWERS" if embedded else "IS_SOLUTION_FOR"
    require_link(
        solution_carrier,
        relation,
        target_ref,
        "solution",
        result["solution"]["source"],
    )
    if (
        not isinstance(model_manifest["boundaries"], dict)
        or not model_manifest["boundaries"]
    ):
        issues.insert(0, "manifest: missing or unsupported boundaries")
    result["issues"] = issues
    return result


def _require_tier(carrier, role, tier, source):
    actual = carrier.metadata.get("tier")
    if type(actual) is not int or actual != tier:
        raise SourceError(
            role, source, "tier", f"{role} must have Tier {tier}"
        )


def load_formal_claim(root, component_id, role, pin):
    """Load one pinned Contract or Solution without its companion Specs."""
    if role not in ("contract", "solution"):
        raise ValueError(f"expected Contract or Solution role, got {role!r}")
    return _load_formal_claim(
        root, component_id, role, pin, 0 if role == "contract" else None
    )


def _carrier_template(carrier, source, role):
    context = carrier.metadata.get("context")
    if not isinstance(context, dict):
        raise SourceError(
            role, source, "context", "expected a Header context mapping"
        )
    return context.get("template")


def _load_formal_claim(root, component_id, role, pin, tier):
    carrier, source = read_source(root, pin, role)
    if tier is None:
        tier = carrier.metadata.get("tier")
        if type(tier) is not int or tier not in (0, 1):
            raise SourceError(
                role, source, "tier", "solution must have Tier 0 or Tier 1"
            )
    _require_tier(carrier, role, tier, source)
    template = _carrier_template(carrier, source, role)
    if role == "contract" and template != "component_contract":
        raise SourceError(
            role, source, "context.template", "expected Component Contract"
        )
    if role == "solution":
        allowed = {"solution"} if tier == 0 else {"decision", "solution"}
        if not isinstance(template, str) or template.casefold() not in allowed:
            message = (
                "expected Solution"
                if tier == 0
                else "expected Solution or Decision"
            )
            raise SourceError(role, source, "context.template", message)
    if source["container_component"] != component_id:
        raise SourceError(
            role,
            source,
            "container.component",
            f"{role} component does not match",
        )
    try:
        claims = list(formal_claim_fences(carrier.body))
    except ValueError as error:
        raise SourceError(role, source, "claim", str(error)) from error
    return (
        carrier,
        {"source": source, "claims": claims},
        _claim_issues(role, claims),
    )


def _claim_issues(role, claims):
    if not claims:
        return [f"{role}: missing formal claim"]
    return [
        f"{role}: unsupported formal claim language {language!r}"
        for language, source in claims
        if not recognized_claim(role, language, source)
    ]


def load_manifest(root, component_id, pin):
    """Read one formal Component Manifest and any embedded public Contract."""
    carrier, source = read_source(root, pin, "manifest")
    if _carrier_template(carrier, source, "manifest") != "component_manifest":
        raise SourceError(
            "manifest",
            source,
            "context.template",
            "expected Component Manifest, not a Seed or another template",
        )
    try:
        contract_claims = component_contract_fences(carrier.body)
    except ValueError as error:
        raise SourceError(
            "manifest", source, "formal_contract", str(error)
        ) from error
    tier, fields = _manifest_fields(carrier, source, component_id)
    manifest = {
        "source": source,
        "tier": tier,
        "fields": fields,
        "boundaries": fields.get("boundaries"),
    }
    if contract_claims is not None:
        manifest["contract"] = {
            "source": source,
            "claims": list(contract_claims),
            "public": True,
        }
        manifest["contract_issues"] = _claim_issues(
            "contract", contract_claims
        )
    return manifest


def _manifest_fields(carrier, source, component_id):
    tier = carrier.metadata.get("tier")
    if type(tier) is not int or tier not in (1, 4):
        raise SourceError(
            "manifest", source, "tier", "manifest must have Tier 1 or Tier 4"
        )
    if tier == 4:
        tokens = MarkdownIt("commonmark").parse(carrier.body)
        if not any(
            token.type == "heading_open"
            and token.tag == "h2"
            and token.level == 0
            and tokens[index + 1].content.strip().casefold()
            == "formal manifest"
            for index, token in enumerate(tokens)
        ):
            raise SourceError(
                "manifest",
                source,
                "formal_manifest",
                "missing Python Formal Manifest",
            )
    try:
        fields, _ = parse_component_manifest(carrier.body, tier=tier)
    except ValueError as error:
        raise SourceError(
            "manifest", source, "formal_manifest", str(error)
        ) from error
    if fields.get("component_id") != component_id:
        raise SourceError(
            "manifest",
            source,
            "component_id",
            "Manifest component does not match",
        )
    return tier, fields
