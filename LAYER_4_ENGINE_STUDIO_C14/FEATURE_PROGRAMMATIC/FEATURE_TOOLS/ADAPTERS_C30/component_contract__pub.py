"""Read authored active Component Contracts."""
import re

from markdown_it import MarkdownIt

from .atom_reference__pub import derive_atom_ref
from .native_carrier_header__pub import native_header_view
from .native_carrier_placement__pub import spec_lens_directories


def read_component_contract(path, carrier, parent, prefix):
    """Return validated fields, or None for an inactive or non-Contract carrier."""
    metadata = carrier.metadata
    context = metadata.get('context', {})
    state = metadata.get('state', {})
    if not isinstance(context, dict) or context.get('template') != 'component_contract':
        return None
    if not isinstance(state, dict) or state.get('status') != 'active':
        return None
    header = native_header_view(metadata)
    context = header['context']
    atom, version = header['identity']['atom_id'], state.get('version')
    if (metadata.get('atom_family') != 'SPEC' or context.get('tier') != 1
            or type(context.get('tier')) is not int or parent is None
            or context.get('container') != {'component': parent}
            or not isinstance(context.get('lens'), str) or not context['lens'].strip()
            or not isinstance(atom, str) or not re.fullmatch(rf'{re.escape(prefix)}-S-[0-9]+', atom)
            or type(version) is not int or version < 1):
        raise ValueError(f'Invalid Component Contract identity or parent: {path}')
    spec_lens_directories(context['lens'])
    tokens = MarkdownIt('commonmark').parse(carrier.body)
    summaries = [i for i, token in enumerate(tokens) if token.type == 'heading_open'
                 and token.tag == 'h2' and token.level == 0 and tokens[i + 1].content.strip() == 'Summary']
    if len(summaries) != 1:
        raise ValueError(f'Component Contract requires one Summary: {path}')
    summary = summaries[0]
    if not (summary + 4 < len(tokens) and tokens[summary + 4].type == 'inline'
            and tokens[summary + 3].type == 'paragraph_open' and tokens[summary + 4].content.strip()):
        raise ValueError(f'Component Contract requires Summary prose: {path}')
    headings = [i for i, token in enumerate(tokens) if token.type == 'heading_open'
                and token.tag == 'h2' and token.level == 0 and tokens[i + 1].content.strip() == 'Guarantee']
    if len(headings) != 1:
        raise ValueError(f'Component Contract requires one Guarantee: {path}')
    start = headings[0]
    end = next((i for i in range(start + 1, len(tokens)) if tokens[i].type == 'heading_open'
                and tokens[i].level == 0 and tokens[i].tag in {'h1', 'h2'}), len(tokens))
    section = tokens[start + 1:end]
    if not any(t.type == 'inline' and t.content.strip() and i and section[i - 1].type == 'paragraph_open'
               for i, t in enumerate(section)):
        raise ValueError(f'Component Contract requires Guarantee prose: {path}')
    lines = carrier.body.splitlines()
    end_line = tokens[end].map[0] if end < len(tokens) else len(lines)
    guarantee = '\n'.join(lines[tokens[start].map[1]:end_line]).strip()
    return {'atom_id': atom, 'component_id': parent, 'ref_id': derive_atom_ref(atom, version, 'active'),
            'version': version, 'guarantee': guarantee}
