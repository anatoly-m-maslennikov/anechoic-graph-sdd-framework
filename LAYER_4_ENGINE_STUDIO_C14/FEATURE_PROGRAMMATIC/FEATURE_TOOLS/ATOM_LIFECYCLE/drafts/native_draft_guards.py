"""Validate native Draft ownership, contracts, and summaries."""

from hashlib import sha256 as sha256
import ast
from pathlib import Path as Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    native_header_view,
    native_carrier_path,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    DRAFT_DIRECTORY as DRAFT_DIRECTORY,
    TICKET_DIRECTORY as TICKET_DIRECTORY,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_carrier as parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS as CEILINGS,
    ReadContext as ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_slug,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    parse_content,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    parse_subject_expression,
    render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.components__shared import (
    parse_typed_manifest_node,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.concern.continuant_concern__pub import (
    CONTINUANT_LENS,
    continuant_model_subject,
    implicit_continuant_node,
    validate_continuant_variant,
)
from markdown_it import MarkdownIt

from .. import common
from .native_draft_owner import _check_owner as _check_owner
from .native_draft_owner import _checked_owner_path as _checked_owner_path


_SUMMARY = re.compile(
    r"(?m)^#{1,2} Summary[ \t]*\r?\n(?:[ \t]*\r?\n)*([^\r\n]+)[ \t]*(?=\r?$)"
)


def is_c9_typed_manifest(header):
    view = native_header_view(header)
    context = view.get("context", {})
    template = context.get("template")
    return (
        header.get("atom_family") == "SPEC"
        and context.get("container") == {"component": "C9"}
        and template
        in {"manifest_node", "manifest_property", "manifest_relation"}
        and (
            context.get("lens") in {"SPEC", CONTINUANT_LENS}
            or (
                context.get("lens") == "DES"
                and template == "manifest_property"
            )
        )
    )


def _has_formal_declaration(body):
    sections = parse_content(body)
    claims = [
        s for s in sections if s["property_path"] == ["claim", "formal_claim"]
    ]
    if len(claims) != 1:
        return False
    tokens = MarkdownIt("commonmark").parse(claims[0]["direct_markdown"] or "")
    if (
        len(tokens) != 1
        or tokens[0].type != "fence"
        or tokens[0].info.strip() != "python"
    ):
        return False
    try:
        return parse_native_model_claim(tokens[0].content) is not None
    except ValueError:
        return False


def _validate_c9_typed_manifest(header, body):
    try:
        _validate_c9_content(header, body)
    except (ValueError, TypeError, KeyError, SyntaxError, IndexError) as error:
        raise common.InputError(
            "target", "Invalid typed Model scope, Concern, or Formal Manifest."
        ) from error


def _validate_c9_content(header, body):
    sections = parse_content(body)
    scopes = [s for s in sections if s["property_path"] == ["claim_scope"]]
    manifests = [
        s for s in sections if s["property_path"] == ["formal_manifest"]
    ]
    template = native_header_view(header)["context"]["template"]
    continuant = (
        native_header_view(header)["context"].get("lens") == CONTINUANT_LENS
    )
    if continuant:
        continuant_model_subject(header.get("concern"))
    if continuant and template == "manifest_node" and not manifests:
        if scopes:
            raise ValueError(
                "Continuant Declaration cannot contain Claim scope"
            )
        implicit_continuant_node(header.get("concern"))
        return
    if (
        len(scopes) > 1
        or (continuant and scopes)
        or (not continuant and not scopes and template != "manifest_property")
        or len(manifests) != 1
        or manifests[0]["heading_level"] != 2
    ):
        raise ValueError("Missing typed scope or manifest")
    if scopes:
        _validate_model_scope(scopes[0])
    if any(
        len(s["property_path"]) > 1
        for s in sections
        if s["property_path"][:1] == ["formal_manifest"]
    ):
        raise ValueError("Nested Formal Manifest")
    source = _typed_manifest_source(manifests[0])
    if continuant:
        validate_continuant_variant(header.get("concern"), template, source)
    _validate_typed_declaration(
        source,
        template,
        unscoped=not scopes and not continuant,
    )


def _validate_model_scope(item):
    scope = (item["direct_markdown"] or "").strip()
    expression = parse_subject_expression(
        scope, subject_profile="approved"
    ).expression
    if (
        not scope.startswith("MODEL//ANECHOIC <+ ")
        or render_subject(expression) != scope
    ):
        raise ValueError("Invalid Model scope")


def _typed_manifest_source(manifest):
    markdown = manifest["direct_markdown"] or ""
    tokens = MarkdownIt("commonmark").parse(markdown)
    if (
        len(tokens) != 1
        or tokens[0].type != "fence"
        or tokens[0].info.strip() != "python anechoic-edsl"
        or tokens[0].map is None
        or markdown.splitlines()[tokens[0].map[1] - 1].strip()
        != tokens[0].markup
    ):
        raise ValueError("Invalid typed Python fence")
    return tokens[0].content


def _validate_typed_declaration(source, template, *, unscoped):
    tree = ast.parse(source)
    is_node = template == "manifest_node"
    if is_node and len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
        parse_typed_manifest_node(source)
        return
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    bases = {
        "manifest_property": {"Property"},
        "manifest_relation": {"Relation"},
    }
    if (
        len(classes) != 1
        or classes[0].decorator_list
        or classes[0].keywords
        or any(not isinstance(base, ast.Name) for base in classes[0].bases)
    ):
        raise ValueError("Invalid typed class")
    class_bases = {base.id for base in classes[0].bases}
    allowed = (ast.ImportFrom, ast.ClassDef)
    if is_node and class_bases == {"NodeConstraints"}:
        allowed += (ast.FunctionDef,)
    if (
        any(not isinstance(node, allowed) for node in tree.body)
        or (is_node and class_bases & {"Property", "Relation"})
        or (
            not is_node
            and (class_bases != bases[template] or len(classes[0].bases) != 1)
        )
    ):
        raise ValueError("Template and typed class differ")
    if unscoped:
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed._package__shared import (
            _field_assignments,
        )

        fields, _ = _field_assignments(classes[0], "Property")
        if "bearer" not in fields or "axis" in fields:
            raise ValueError(
                "An unscoped Property requires a bearer and "
                "cannot declare an axis"
            )


def _summary(body):
    matches = list(_SUMMARY.finditer(body))
    if len(matches) != 1 or not matches[0].group(1).strip():
        raise common.InputError(
            "summary", "Exactly one nonempty Summary is required."
        )
    return matches[0].group(1)


def _native_slug(body):
    summary = _summary(body)
    if not summary.isprintable():
        raise common.InputError(
            "summary", "Summary must contain printable characters."
        )
    return carrier_slug(
        "".join(char if char.isascii() else "-" for char in summary)
    )


def _reject_component_contract(template, field):
    if template == "component_contract":
        raise common.InputError(
            field, "Add the Component Contract to the Component Manifest."
        )


def _check_first_spec(selection, header, body, path, owner):
    summary = _summary(body)
    if is_c9_typed_manifest(header):
        _validate_c9_typed_manifest(header, body)
    if "atom_family" in header:
        try:
            projected = native_carrier_path(
                header,
                summary,
                project_root=selection.control_root,
                owner_directory=owner,
            )
        except ValueError as error:
            raise common.InputError(
                "target",
                "Spec Draft Header or Summary cannot be projected to a path.",
            ) from error
        if path != projected:
            raise common.InputError(
                "target",
                "Spec Draft path disagrees with its Header and Summary.",
            )
