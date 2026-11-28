"""Read native Component claims without executing authored code."""

import ast
import json

from markdown_it import MarkdownIt

from ...model.claims.native_model_claim__pub import parse_manifest_declaration
from ...model.formal_claim__pub import formal_claim
from ...model.claims.native_model_claim_values import _dictionary


_CANONICAL_SECTIONS = {
    "component identity",
    "component boundaries",
    "component contract",
}
_MANIFEST_SECTIONS = _CANONICAL_SECTIONS | {"summary", "purpose"}


def _claim_headings(tokens, body):
    in_claim = False
    lines = body.splitlines()
    for i, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        title = tokens[i + 1].content.strip()
        level = int(token.tag[1:])
        if level == 2:
            in_claim = title == "Claim"
        elif in_claim and level == 3:
            end = next(
                (
                    t.map[0]
                    for t in tokens[i + 1 :]
                    if t.type == "heading_open"
                ),
                len(lines),
            )
            yield title, "\n".join(lines[token.map[1] : end]).strip()


def _formal_component_instance(tokens, body, source=None):
    if source is None:
        if not any(
            token.type == "heading_open"
            and tokens[i + 1].content.strip().casefold() == "formal claim"
            for i, token in enumerate(tokens)
        ):
            return None
        source = formal_claim(body)
    return parse_manifest_declaration(
        source,
        entity_name="Component Manifest",
        class_name="ComponentManifest",
    )


def _legacy_manifest_fields(tokens, body):
    fields = _formal_component_instance(tokens, body)
    if fields is not None:
        return fields
    sections = {}
    for title, value in _claim_headings(tokens, body):
        key = {
            "Component ID": "component_id",
            "Name": "name",
            "Layer": "layer",
            "Lens Whitelist": "lens_whitelist",
        }.get(title)
        if key is None or key in sections:
            raise ValueError("Unknown or duplicate Component Manifest field")
        sections[key] = (
            json.loads(value) if key in {"layer", "lens_whitelist"} else value
        )
    if not {"component_id", "name"} <= sections.keys():
        raise ValueError("Missing Component Manifest fields")
    return sections


def _parse_legacy_manifest(tokens, body):
    headings = _manifest_headings(tokens)
    lines = body.splitlines()

    def section_end(index):
        return next(
            (
                t.map[0]
                for t in tokens[index + 1 :]
                if t.type == "heading_open"
                and t.tag in {"h1", "h2"}
                and t.level == 0
            ),
            len(lines),
        )

    purpose_index = headings.get("purpose")
    purpose = (
        "\n".join(
            lines[tokens[purpose_index].map[1] : section_end(purpose_index)]
        ).strip()
        or None
        if purpose_index is not None
        else None
    )
    formal_index = headings.get("formal manifest")
    if formal_index is not None:
        if any(
            t.type == "heading_open"
            and t.tag == "h2"
            and t.level == 0
            and tokens[i + 1].content.strip().casefold() == "claim"
            for i, t in enumerate(tokens)
        ):
            raise ValueError("Ambiguous Component Manifest formal sections")
        end = section_end(formal_index)
        section = [
            t for t in tokens[formal_index + 1 :] if t.map and t.map[0] < end
        ]
        return _formal_component_instance(
            tokens, body, _formal_fence(section)
        ), purpose
    return _legacy_manifest_fields(tokens, body), purpose


def _manifest_headings(tokens):
    headings = {}
    for i, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        title = tokens[i + 1].content.strip().casefold()
        if title in {"purpose", "formal manifest"}:
            if title == "purpose" and (token.tag != "h2" or token.level != 0):
                continue
            if token.tag != "h2" or token.level != 0 or title in headings:
                raise ValueError(
                    "Expected unique top-level Component Manifest headings"
                )
            headings[title] = i
    return headings


def _canonical_sections(tokens):
    headings = [
        (i, tokens[i + 1].content.strip().casefold())
        for i, token in enumerate(tokens)
        if token.type == "heading_open"
    ]
    if _CANONICAL_SECTIONS.isdisjoint(title for _, title in headings):
        return None
    if any(
        title in {"claim", "formal manifest"}
        and tokens[i].level == 0
        and tokens[i].tag == "h2"
        for i, title in headings
    ):
        raise ValueError("Ambiguous Component Manifest formal sections")
    boundaries = [
        i
        for i, _ in headings
        if tokens[i].level == 0 and tokens[i].tag in {"h1", "h2"}
    ]
    ends = dict(zip(boundaries, boundaries[1:] + [len(tokens)], strict=True))
    sections = {}
    for i, title in headings:
        if title not in _MANIFEST_SECTIONS:
            continue
        if i not in ends or tokens[i].tag != "h2" or title in sections:
            raise ValueError(
                (
                    "Expected unique top-level Component Manifest heading: "
                    f"{title}"
                )
            )
        sections[title] = tokens[i + 3 : ends[i]]
    if "component identity" not in sections:
        raise ValueError(
            "Missing Component Manifest heading: Component Identity"
        )
    return sections


def _section_fences(sections, title):
    section = sections[title]
    fences = [token for token in section if token.type == "fence"]
    if title == "component contract":
        if not fences:
            _require_prose(section, title)
    elif not fences or any(token.type == "heading_open" for token in section):
        raise ValueError(f"Expected nonempty fences directly under {title}")
    if any(
        token.level != 0 or not token.info.strip() or not token.content.strip()
        for token in fences
    ):
        raise ValueError(f"Expected nonempty fences directly under {title}")
    return tuple(
        (token.info.strip().casefold(), token.content) for token in fences
    )


def _python_section(sections, title):
    fences = _section_fences(sections, title)
    if len(fences) != 1 or fences[0][0] != "python":
        raise ValueError(f"Expected one Python fence under {title}")
    return fences[0][1]


def _literal_boundaries(source):
    try:
        node = ast.parse(source, mode="eval").body
    except SyntaxError as error:
        raise ValueError(
            "Expected a literal mapping under Component Boundaries"
        ) from error
    if not isinstance(node, ast.Dict) or any(
        isinstance(item, (ast.Name, ast.Call)) for item in ast.walk(node)
    ):
        raise ValueError(
            "Expected a literal mapping under Component Boundaries"
        )
    return _dictionary(node, set())


def _require_prose(section, title):
    if not any(
        token.type == "paragraph_open" and section[i + 1].content.strip()
        for i, token in enumerate(section)
    ):
        raise ValueError(f"Expected prose under {title}")


def parse_component_manifest(body, *, tier=None):
    tokens = MarkdownIt("commonmark").parse(body)
    sections = _canonical_sections(tokens)
    if sections is None:
        if tier == 1:
            raise ValueError(
                "Tier 1 Component Manifest requires canonical sections"
            )
        return _parse_legacy_manifest(tokens, body)
    if tier == 4:
        raise ValueError("Canonical Component Manifest requires Tier 1")
    for title in ("summary", "purpose"):
        if title in sections:
            _require_prose(sections[title], title)
    fields = _formal_component_instance(
        tokens, body, _python_section(sections, "component identity")
    )
    if (
        fields.keys() - {"component_id", "name", "layer", "lens_whitelist"}
        or any(
            not isinstance(fields.get(key), str) or not fields[key].strip()
            for key in ("component_id", "name")
        )
        or (
            fields.get("layer") is not None
            and type(fields["layer"]) is not int
        )
    ):
        raise ValueError("Invalid Component Identity fields")
    if "component boundaries" in sections:
        fields["boundaries"] = _literal_boundaries(
            _python_section(sections, "component boundaries")
        )
    if "component contract" in sections:
        _section_fences(sections, "component contract")
    purpose = sections.get("purpose")
    if purpose is None:
        return fields, None
    return fields, "\n".join(
        body.splitlines()[
            purpose[0].map[0] : max(
                token.map[1] for token in purpose if token.map
            )
        ]
    ).strip()


def parse_component_manifest_fields(body, *, tier=None):
    return parse_component_manifest(body, tier=tier)[0]


def component_contract_fences(body):
    """Return ordered inline Contract fences when present."""
    sections = _canonical_sections(MarkdownIt("commonmark").parse(body))
    if sections is not None and "component contract" in sections:
        return _section_fences(sections, "component contract")
    return None


def _formal_fence(section):
    fences = [t for t in section if t.type == "fence"]
    if (
        len(fences) != 1
        or fences[0].info.strip().casefold() != "python"
        or fences[0].level != 0
        or any(t.type == "heading_open" for t in section)
    ):
        raise ValueError("Expected one Python Formal Manifest")
    return fences[0].content
