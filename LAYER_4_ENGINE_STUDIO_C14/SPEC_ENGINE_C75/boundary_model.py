"""Bind a Component's independent formal Manifest, Contract and Solution."""
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    formal_claim_fences,
    parse_component_manifest,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import derive_atom_ref
from markdown_it import MarkdownIt

from .boundary_sources import read_source, recognized_claim, require_link


def load_boundary_model(root, component_id, manifest, contract, solution):
    """Load exact source pins; preserve unparsed claims and report unsupported input."""
    model_manifest = load_manifest(root, component_id, manifest)
    carriers = {}
    result = {'component_id': component_id, 'manifest': model_manifest}
    issues = []
    for role, pin in (('contract', contract), ('solution', solution)):
        carriers[role], result[role], claim_issues = load_formal_claim(root, component_id, role, pin)
        issues.extend(claim_issues)
    require_link(carriers['contract'], 'ANSWERS', manifest['atom_id'])
    contract_ref = derive_atom_ref(contract['atom_id'], contract['version'], contract['status'])
    require_link(carriers['solution'], 'IS_SOLUTION_FOR', contract_ref)
    if not isinstance(model_manifest['boundaries'], dict) or not model_manifest['boundaries']:
        issues.insert(0, 'manifest: missing or unsupported boundaries')
    result['issues'] = issues
    return result


def _require_tier(carrier, role, tier):
    actual = carrier.metadata.get('tier')
    if type(actual) is not int or actual != tier:
        raise ValueError(f'{role} must have Tier {tier}')


def load_formal_claim(root, component_id, role, pin):
    """Load one pinned Contract or Solution without its companion Specs."""
    if role not in ('contract', 'solution'):
        raise ValueError(f'expected Contract or Solution role, got {role!r}')
    carrier, source = read_source(root, pin, role)
    _require_tier(carrier, role, 0 if role == 'contract' else 1)
    template = carrier.metadata.get('context', {}).get('template')
    if role == 'contract' and template != 'component_contract':
        raise ValueError('expected Component Contract')
    if role == 'solution' and (not isinstance(template, str) or template.casefold() not in {'decision', 'solution'}):
        raise ValueError('expected Solution or Decision')
    if source['container_component'] != component_id:
        raise ValueError(f'{role} component does not match')
    claims, issues = _claims(role, carrier.body)
    return carrier, {'source': source, 'claims': claims}, issues


def _claims(role, body):
    claims = list(formal_claim_fences(body))
    if not claims:
        return claims, [f'{role}: missing formal claim']
    return claims, [f'{role}: unsupported formal claim language {language!r}'
                    for language, source in claims if not recognized_claim(role, language, source)]


def load_manifest(root, component_id, pin):
    """Read one formal Component Manifest independently of its Contract and Solution."""
    carrier, source = read_source(root, pin, 'manifest')
    if carrier.metadata.get('context', {}).get('template') != 'component_manifest':
        raise ValueError('expected Component Manifest, not a Seed or another template')
    _require_tier(carrier, 'manifest', 4)
    tokens = MarkdownIt('commonmark').parse(carrier.body)
    if not any(token.type == 'heading_open' and token.tag == 'h2' and token.level == 0
               and tokens[index + 1].content.strip().casefold() == 'formal manifest'
               for index, token in enumerate(tokens)):
        raise ValueError('missing Python Formal Manifest')
    fields, _ = parse_component_manifest(carrier.body)
    if fields.get('component_id') != component_id:
        raise ValueError('Manifest component does not match')
    return {'source': source, 'fields': fields, 'boundaries': fields.get('boundaries')}
