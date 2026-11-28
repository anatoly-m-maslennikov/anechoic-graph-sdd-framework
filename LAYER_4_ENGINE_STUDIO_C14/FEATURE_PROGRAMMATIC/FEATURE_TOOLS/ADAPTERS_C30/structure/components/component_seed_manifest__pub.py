"""Read active native Component Seed Manifests \
without executing their claims."""

import re

from markdown_it import MarkdownIt

from ...model.claims.native_model_claim__pub import parse_manifest_declaration
from ...structure.code_access_rules__pub import parse_code_access
from ...carriers.content.atom_reference__pub import derive_atom_ref
from ...carriers.header.native_carrier_header__pub import native_header_view


def _fields(body):
    sections = _sections(body)
    allowed = ("Formal Manifest", "Purpose", "Contract", "Solution")
    if (
        not sections
        or next(iter(sections)) != "Formal Manifest"
        or tuple(sections)
        != tuple(name for name in allowed if name in sections)
        or any(
            not value
            for name, value in sections.items()
            if name != "Formal Manifest"
        )
    ):
        raise ValueError(
            "Expected Formal Manifest and optional nonempty Purpose, "
            "Contract and Solution sections in order"
        )
    fields = parse_manifest_declaration(
        sections["Formal Manifest"],
        entity_name="Component Seed Manifest",
        class_name="ComponentSeedManifest",
    )
    if fields.keys() - {"component_seed_id", "tier", "boundaries"}:
        raise ValueError(
            "Invalid Component Seed Manifest fields; prose belongs in sections"
        )
    if not isinstance(
        fields.get("component_seed_id"), str
    ) or not re.fullmatch(r"CS[0-9]+", fields["component_seed_id"]):
        raise ValueError("Invalid Component Seed Manifest ID")
    parse_code_access(fields.get("boundaries"))
    return fields | {
        name.lower(): value
        for name, value in sections.items()
        if name != "Formal Manifest"
    }


def _sections(body):
    tokens = MarkdownIt("commonmark").parse(body)
    lines = body.splitlines()
    sections = {}
    for i, token in enumerate(tokens):
        if (
            token.type != "heading_open"
            or token.tag != "h2"
            or token.level != 0
        ):
            continue
        title = tokens[i + 1].content.strip()
        if title in sections:
            raise ValueError("Duplicate Component Seed Manifest section")
        end = next(
            (
                j
                for j in range(i + 1, len(tokens))
                if tokens[j].type == "heading_open"
                and tokens[j].tag in {"h1", "h2"}
                and tokens[j].level == 0
            ),
            len(tokens),
        )
        if title == "Formal Manifest":
            content = tokens[i + 3 : end]
            if (
                len(content) != 1
                or content[0].type != "fence"
                or content[0].level != 0
                or content[0].info.strip().casefold() != "python"
            ):
                raise ValueError(
                    "Expected one direct Python Formal Manifest fence"
                )
            sections[title] = content[0].content
        else:
            end_line = tokens[end].map[0] if end < len(tokens) else len(lines)
            sections[title] = "\n".join(lines[token.map[1] : end_line]).strip()
    return sections


def read_component_seed_manifest(path, carrier, parent, prefix):
    """Return validated source fields, or None for an inactive source."""
    header = native_header_view(carrier.metadata)
    context, state, identity = (
        header.get(name) for name in ("context", "state", "identity")
    )
    if not all(
        isinstance(group, dict) for group in (context, state, identity)
    ):
        raise ValueError(f"Invalid Component Seed Manifest header: {path}")
    if state.get("status") != "active":
        return None
    atom, version = identity.get("atom_id"), state.get("version")
    if (
        parent is None
        or context.get("template") != "component_seed_manifest"
        or context.get("lens") != "SPEC"
        or context.get("container") != {"component": parent}
        or not isinstance(atom, str)
        or not re.fullmatch(rf"{re.escape(prefix)}-S-[0-9]+", atom)
        or type(version) is not int
        or version < 1
    ):
        raise ValueError(
            f"Invalid Component Seed Manifest identity or parent: {path}"
        )
    return {
        "atom_id": atom,
        "ref_id": derive_atom_ref(atom, version, state["status"]),
        "version": version,
        **_fields(carrier.body),
    }
