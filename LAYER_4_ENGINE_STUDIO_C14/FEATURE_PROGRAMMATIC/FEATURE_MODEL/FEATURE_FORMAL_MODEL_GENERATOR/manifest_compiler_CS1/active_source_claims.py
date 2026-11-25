"""Read the Model scopes and typed manifests from selected carriers."""

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import _native_claim_text
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    SubjectNotationError as _subject_SubjectNotationError,
    parse_content,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
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
