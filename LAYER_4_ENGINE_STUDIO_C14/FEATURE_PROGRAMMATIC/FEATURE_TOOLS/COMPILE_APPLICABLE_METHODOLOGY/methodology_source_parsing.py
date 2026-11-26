"""Parse source Carrier metadata for the Methodology compiler."""

from __future__ import annotations

import re
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import atom_identifier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import header_scalar
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_conflicts import sha256_bytes


class CompileError(Exception):
    """A stable compilation validation failure."""

    def __init__(self, code: str, message: str, **details: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def record(self) -> dict[str, object]:
        result: dict[str, object] = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


def relations_digest(frontmatter: str) -> str:
    """Digest authored Relations without normalizing or rewriting them."""
    return sha256_bytes("\n".join(top_block(frontmatter, "relations")).encode("utf-8"))


def scalar_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def split_frontmatter(data: bytes, path: str) -> tuple[str, bytes]:
    if not data.startswith(b"---\n"):
        raise CompileError("source-frontmatter-missing", "Source Carrier requires YAML frontmatter", path=path)
    boundary = data.find(b"\n---\n", 4)
    if boundary < 0:
        raise CompileError("source-frontmatter-unterminated", "Source Carrier frontmatter is unterminated", path=path)
    try:
        frontmatter = data[4:boundary].decode("utf-8")
        data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CompileError("source-not-utf8", "Source Carrier must be UTF-8", path=path) from error
    return frontmatter, data[boundary + 5 :]


def top_scalar(frontmatter: str, key: str) -> str | None:
    try:
        return header_scalar(frontmatter, key)
    except ValueError as error:
        raise CompileError("source-frontmatter-invalid", "Source Carrier has invalid or conflicting Header properties", key=key) from error


def top_block(frontmatter: str, key: str) -> list[str]:
    lines = frontmatter.splitlines()
    start = next((index for index, line in enumerate(lines) if re.fullmatch(rf"{re.escape(key)}:\s*", line)), None)
    if start is None:
        return []
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line and not line[0].isspace():
            break
        block.append(line)
    return block


def relation_targets(frontmatter: str, kinds: set[str]) -> tuple[str, ...]:
    block = top_block(frontmatter, "relations")
    if not block:
        return ()
    found: set[str] = set()
    current_mapping_kind: str | None = None
    current_list_kind: str | None = None
    collecting_list_targets = False
    for line in block:
        mapping = re.fullmatch(r"  ([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)", line)
        if mapping:
            key, raw = mapping.groups()
            current_mapping_kind = key if key in kinds else None
            current_list_kind = None
            collecting_list_targets = False
            if current_mapping_kind and raw and raw != "[]":
                found.add(scalar_value(raw))
            continue
        list_type = re.fullmatch(r"  -\s*type:\s*(.+?)\s*", line)
        if list_type:
            kind = scalar_value(list_type.group(1))
            current_list_kind = kind if kind in kinds else None
            current_mapping_kind = None
            collecting_list_targets = False
            continue
        list_target_key = re.fullmatch(r"    (?:target|targets):\s*(.*?)\s*", line)
        if list_target_key and current_list_kind:
            raw = list_target_key.group(1)
            collecting_list_targets = not raw
            if raw and raw != "[]":
                found.add(scalar_value(raw))
            continue
        mapping_item = re.fullmatch(r"    -\s*(.+?)\s*", line)
        if mapping_item and current_mapping_kind:
            found.add(scalar_value(mapping_item.group(1)))
            continue
        list_item = re.fullmatch(r"      -\s*(.+?)\s*", line)
        if list_item and current_list_kind and collecting_list_targets:
            found.add(scalar_value(list_item.group(1)))
    return tuple(sorted(value for value in found if value))


def derive_atom_id(path: Path, frontmatter: str) -> str:
    explicit = top_scalar(frontmatter, "atom_id")
    identity = atom_identifier(path.name, explicit)
    if not identity:
        raise CompileError("source-atom-identity-missing", "Cannot derive Source Atom identity", path=path.as_posix())
    return identity


def definition_subject(frontmatter: str, path: str) -> tuple[str | None, str | None, str]:
    role = top_scalar(frontmatter, "role")
    if (matches_named_value(role, "Method") or matches_named_value(role, "Requirement")) and matches_named_value(
        top_scalar(frontmatter, "form"), "Term Definition"
    ):
        return term_definition_subject(frontmatter, path, role)
    return None, None, ""


def _term_namespace(expression):
    namespace = ""
    if isinstance(expression, _subject_RelationChain):
        roots = [_subject_render_subject(endpoint) for endpoint in expression.endpoints[:-1]]
        if any(link.operator != "<+" or link.relation_type is not None
               or link.forward_cardinality is not None or link.reverse_cardinality is not None
               for link in expression.links):
            raise _subject_SubjectNotationError("invalid-namespace", "Invalid Term namespace")
        if roots in (["ANECHOIC_MODEL"], ["MODEL//ANECHOIC"], ["ANECHOIC", "MODEL"]):
            pass
        elif (len(roots) == 1 and isinstance(expression.endpoints[0].head, _subject_Name)
              and expression.endpoints[0].head.value == "MODEL"
              and len(expression.endpoints[0].steps) == 1
              and expression.endpoints[0].steps[0].operator == "//"
              and isinstance(expression.endpoints[0].steps[0].operand, _subject_Name)
              and expression.endpoints[0].value_format is None
              and expression.endpoints[0].value_cardinality is None):
            namespace = roots[0]
        else:
            raise _subject_SubjectNotationError("invalid-namespace", "Invalid Term namespace")
        expression = expression.endpoints[-1]
    return expression, namespace


def term_definition_subject(frontmatter: str, path: str, role: str | None) -> tuple[str, str, str]:
    subject = top_scalar(frontmatter, "topics.main_subject")
    try:
        expression = _subject_parse_subject_expression(subject or "", subject_profile="approved").expression
        expression, namespace = _term_namespace(expression)
        steps = expression.steps if isinstance(expression, _subject_Path) else ()
        legacy_prefix = (
            matches_named_value(role, "Requirement")
            and isinstance(expression, _subject_Path)
            and isinstance(expression.head, _subject_Name) and expression.head.value == "Entity"
            and [(step.operator, step.operand.value) for step in steps[:-1]
                 if isinstance(step.operand, _subject_Name)]
            == [("/", "Object"), ("/", "Continuant"), ("/", "Term")]
            and len(steps) == 4
        )
        if (
            isinstance(expression, _subject_Path)
            and ((isinstance(expression.head, _subject_Name) and expression.head.value == "Term" and len(steps) == 1)
                 or legacy_prefix)
            and steps[-1].operator == "//" and isinstance(steps[-1].operand, _subject_Name)
            and expression.value_format is None and expression.value_cardinality is None
        ):
            term = steps[-1].operand.value
            return term, subject, namespace
    except _subject_SubjectNotationError:
        pass
    raise CompileError(
        "source-subject-path-invalid", "Term Definition requires a Term//Name main Subject",
        path=path, subject_path=subject,
    )
