"""Read active native Package Specs without executing their claims."""

import re

from markdown_it import MarkdownIt

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_FORMAL_MODEL_ENGINE.scope_callback_asset import formal_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access import parse_code_access


def _fields(body):
    tokens = MarkdownIt('commonmark').parse(body)
    lines = body.splitlines()
    sections = {}
    has_formal = False
    for i, token in enumerate(tokens):
        if token.type != 'heading_open':
            continue
        title = tokens[i + 1].content.strip()
        if token.tag == 'h3' and title.casefold() == 'formal claim':
            has_formal = True
        if token.tag != 'h2' or title not in {'Purpose', 'Contract'}:
            continue
        key = title.lower()
        if key in sections:
            raise ValueError('Duplicate Package Spec section')
        end = next((t.map[0] for t in tokens[i + 1:]
                    if t.type == 'heading_open' and t.tag in {'h1', 'h2'}), len(lines))
        sections[key] = '\n'.join(lines[token.map[1]:end]).strip()
    if has_formal:
        claim = parse_native_model_claim(formal_claim(body))
        args = claim['arguments'] if claim and claim['kind'] == 'entity' else {}
        instance = args.get('instance', {})
        if (set(args) != {'entity_name', 'instance'} or args['entity_name'] != 'Package Spec'
                or instance.get('type') != 'PackageSpec'):
            raise ValueError('Expected one formal PackageSpec instance')
        fields = instance['fields']
        if 'package_id' not in fields:
            raise ValueError('Missing formal Package Spec ID')
        if any(fields.get(key) != value for key, value in sections.items()):
            raise ValueError('Package Spec prose and formal fields differ')
    else:
        fields = sections
    if (fields.keys() - {'package_id', 'purpose', 'contract', 'tier', 'boundaries'}
            or any(not isinstance(fields.get(key), str) or not fields[key].strip()
                   for key in ('purpose', 'contract'))):
        raise ValueError('Invalid Package Spec fields')
    parse_code_access(fields.get('boundaries'))
    return fields


def read_package_spec(path, carrier, parent, prefix):
    """Return validated source fields, or None for an inactive source."""
    context, state, identity = (carrier.metadata.get(name) for name in ('context', 'state', 'identity'))
    if not all(isinstance(group, dict) for group in (context, state, identity)):
        raise ValueError(f'Invalid Package Spec header: {path}')
    if state.get('status') != 'active':
        return None
    atom, version = identity.get('atom_id'), state.get('version')
    package_id = context.get('package_id')
    if (parent is None or context.get('template') != 'PKG' or context.get('lens') != 'SPEC'
            or context.get('container') != {'component': parent}
            or not isinstance(package_id, str) or not package_id.strip() or package_id == atom
            or not isinstance(atom, str) or not re.fullmatch(rf'{re.escape(prefix)}-S-[0-9]+', atom)
            or not re.fullmatch(rf'{re.escape(atom)}-SPEC-PKG--.+\.md', path.name)
            or type(version) is not int or version < 1):
        raise ValueError(f'Invalid Package Spec identity or parent: {path}')
    fields = _fields(carrier.body)
    if 'package_id' in fields and fields['package_id'] != package_id:
        raise ValueError(f'Package Spec ID differs from header: {path}')
    return {'atom_id': atom, 'ref_id': f'{atom}@{version}', 'version': version,
            **fields, 'package_id': package_id}
