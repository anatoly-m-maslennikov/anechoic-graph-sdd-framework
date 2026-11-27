"""Read the Model scopes and typed manifests from selected carriers."""

import ast
from pathlib import PurePosixPath
import re

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import _native_claim_text
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    SubjectNotationError as _subject_SubjectNotationError,
    CUSTOM_MODEL_DIRECTORY, PROJECT_CONFIG_DIRECTORY, native_header_view, parse_content,
    parse_native_model_claim,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import is_ontology_model_source
from markdown_it import MarkdownIt


def _claim_subject(body: str, source: str) -> str | None:
    sections = parse_content(body, tolerate_duplicate_siblings=True)
    scopes = [s['direct_markdown'] for s in sections if s['property_path'] == ['claim_scope']]
    if not any(isinstance(scope, str) and 'MODEL//ANECHOIC' in scope for scope in scopes):
        return None
    if len(scopes) != 1 or not isinstance(scopes[0], str):
        raise ValueError(f'{source}: expected one Model Claim scope')
    return _valid_subject(scopes[0].strip(), source)


def _valid_subject(subject: str, source: str) -> str:
    try:
        expression = _subject_parse_subject_expression(subject, subject_profile='approved').expression
    except _subject_SubjectNotationError as error:
        raise ValueError(f'{source}: invalid Model Claim scope') from error
    if _subject_render_subject(expression) != subject or not subject.startswith('MODEL//ANECHOIC <+ '):
        raise ValueError(f'{source}: invalid Model Claim scope')
    return subject


def _custom_claims(body: str, source: str):
    sections = parse_content(body)
    manifests = [s for s in sections if s['property_path'] == ['formal_manifest']]
    declarations = [s for s in sections if s['property_path'][:1] == ['formal_manifest']
                    and len(s['property_path']) == 2]
    if (len(manifests) != 1 or manifests[0]['heading_level'] != 2
            or manifests[0]['direct_markdown'] or not declarations
            or any(s['heading_level'] != 3 for s in declarations)
            or any(len(s['property_path']) > 2 for s in sections if s['property_path'][:1] == ['formal_manifest'])):
        raise ValueError(f'{source}: expected Formal Manifest with direct declaration subsections')
    result = []
    for declaration in declarations:
        text = declaration['direct_markdown'] or ''
        subject, separator, claim = text.strip().partition('\n')
        if not separator:
            raise ValueError(f'{source}: expected Model scope and Python fence')
        subject = _valid_subject(subject.strip(), source)
        result.append((subject, _native_claim_text(claim, source, subject)))
    return result


def _typed_manifest(sections, source, subject, context, typed):
    manifests = [section for section in sections if section['property_path'] == ['formal_manifest']]
    if len(manifests) != 1 or manifests[0]['heading_level'] != 2 or any(
        len(section['property_path']) > 1 for section in sections
        if section['property_path'][:1] == ['formal_manifest']
    ):
        raise ValueError(f'{source}: expected one Formal Manifest block')
    markdown = manifests[0]['direct_markdown'] or ''
    tokens = MarkdownIt('commonmark').parse(markdown)
    if (len(tokens) != 1 or tokens[0].type != 'fence'
            or tokens[0].info.strip() != 'python anechoic-edsl'
            or tokens[0].map is None
            or markdown.splitlines()[tokens[0].map[1] - 1].strip() != tokens[0].markup):
        raise ValueError(f'{source}: expected one closed typed Python fence')
    typed.append((source, subject, tokens[0].content, context.get('template')))


class ModelSourceError(ValueError):
    """Invalid selected Model Atom, with its immutable source identity."""

    def __init__(self, source_path, exact_ref, message, *, code="invalid_model_source", subject=None):
        self.detail = message
        self.stage = "model_compile"
        self.code = code
        self.source_path = source_path
        self.atom_ref = exact_ref
        self.exact_ref = exact_ref
        self.subject = subject
        super().__init__(f"{source_path} ({exact_ref}): {message}")


def _validate_model_row(row, source, exact_ref, seen_paths):
    if not isinstance(row, dict) or set(row) != {"source_path", "exact_ref", "metadata", "body"}:
        raise ValueError("invalid Model source row fields")
    if not isinstance(source, str) or not isinstance(exact_ref, str):
        raise ValueError("invalid Model source identity")
    relative = PurePosixPath(source)
    parts = relative.parts
    if (relative.is_absolute() or str(relative) != source or ".." in parts
            or "\\" in source or source in seen_paths):
        raise ValueError("invalid or duplicate Model source path")
    seen_paths.add(source)
    is_c9 = is_ontology_model_source(relative)
    is_custom = (len(parts) == 3 and parts[0] in {PROJECT_CONFIG_DIRECTORY, "__PROJECT_CONFIG", "002_PROJECT_CONFIG"}
                 and parts[1] == CUSTOM_MODEL_DIRECTORY)
    if not (is_c9 or is_custom) or not isinstance(row["metadata"], dict) or not isinstance(row["body"], str):
        raise ValueError("invalid Model source path or carrier")
    header = native_header_view(row["metadata"])
    identity, state = header.get("identity"), header.get("state")
    if (not isinstance(identity, dict) or not isinstance(state, dict)
            or exact_ref != f'{identity.get("atom_id")}@{state.get("version")}'):
        raise ValueError("exact reference disagrees with carrier")
    return is_custom


def _source_error(source, code, subject, message):
    path, _, _ = source.rpartition('@')
    return ModelSourceError(path or source, None, message, code=code, subject=subject)


def is_project_model_source(source):
    return PurePosixPath(source.rsplit('@', 1)[0]).parts[1:2] == (CUSTOM_MODEL_DIRECTORY,)


def extend_current_status(source, subject, claim, records, addresses):
    """Add Project Current Ticket values to the base Status declaration."""
    ticket = addresses.get('TicketAtom')
    if ticket is None or subject != f'MODEL//ANECHOIC <+ {ticket}.Header.State.Status':
        return False
    arguments = parse_native_model_claim(claim)['arguments']
    additions = arguments.get('allowed_values', ())
    if (not additions or any(not isinstance(value, str)
                             or not re.fullmatch(r'[a-z][a-z0-9_]*', value)
                             or value in {'draft', 'ready', 'active', 'archived', 'in_progress'} for value in additions)
            or len(additions) != len(set(additions))):
        raise _source_error(source, 'invalid_status_extension', subject,
                            'Project Config must add distinct Current Status values')
    for index, (base_source, base_subject, base_claim) in enumerate(records):
        if base_subject != subject or not is_ontology_model_source(PurePosixPath(base_source.rsplit('@', 1)[0])):
            continue
        base = parse_native_model_claim(base_claim)['arguments']
        base_values = base.get('allowed_values', ())
        if (not base_values
                or {key: value for key, value in arguments.items() if key != 'allowed_values'}
                != {key: value for key, value in base.items() if key != 'allowed_values'}
                or set(additions).intersection(base_values)):
            raise _source_error(source, 'invalid_status_extension', subject,
                                'Project Config Status declarations may only add values')
        tree = ast.parse(base_claim)
        declaration = next(item.value for item in tree.body if isinstance(item, ast.Expr))
        allowed = next(item for item in declaration.keywords if item.arg == 'allowed_values')
        allowed.value = ast.parse(repr((*base_values, *additions)), mode='eval').body
        records[index] = (base_source, subject, ast.unparse(tree) + '\n')
        return True
    raise _source_error(source, 'invalid_status_extension', subject, 'Base Model Status declaration is missing')
