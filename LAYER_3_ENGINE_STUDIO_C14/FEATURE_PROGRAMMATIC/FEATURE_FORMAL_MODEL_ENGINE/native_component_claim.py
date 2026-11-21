"""Read native Component claims without executing authored code."""

import json
import re

from markdown_it import MarkdownIt

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_FORMAL_MODEL_ENGINE.scope_callback_asset import formal_claim


def _claim_headings(tokens, body):
    in_claim = False
    lines = body.splitlines()
    for i, token in enumerate(tokens):
        if token.type != 'heading_open':
            continue
        title = tokens[i + 1].content.strip()
        level = int(token.tag[1:])
        if level == 2:
            in_claim = title == 'Claim'
        elif in_claim and level == 3:
            end = next((t.map[0] for t in tokens[i + 1:] if t.type == 'heading_open'), len(lines))
            yield title, '\n'.join(lines[token.map[1]:end]).strip()


def _formal_instance(tokens, body, entity_name, instance_type):
    if not any(token.type == 'heading_open' and tokens[i + 1].content.strip().casefold() == 'formal claim'
               for i, token in enumerate(tokens)):
        return None
    claim = parse_native_model_claim(formal_claim(body))
    args = claim['arguments'] if claim and claim['kind'] == 'entity' else {}
    instance = args.get('instance', {})
    if (set(args) != {'entity_name', 'instance'} or args['entity_name'] != entity_name
            or instance.get('type') != instance_type):
        raise ValueError(f'Expected one formal {instance_type} instance')
    return instance['fields']


def parse_component_manifest_fields(body):
    tokens = MarkdownIt('commonmark').parse(body)
    fields = _formal_instance(tokens, body, 'Component Manifest', 'ComponentManifest')
    if fields is not None:
        return fields
    sections = {}
    for title, value in _claim_headings(tokens, body):
        key = {'Component ID': 'component_id', 'Name': 'name', 'Layer': 'layer',
               'Lens Whitelist': 'lens_whitelist'}.get(title)
        if key is None or key in sections:
            raise ValueError('Unknown or duplicate Component Manifest field')
        sections[key] = json.loads(value) if key in {'layer', 'lens_whitelist'} else value
    if not {'component_id', 'name'} <= sections.keys():
        raise ValueError('Missing Component Manifest fields')
    return sections


def parse_component_purpose_id(body):
    tokens = MarkdownIt('commonmark').parse(body)
    fields = _formal_instance(tokens, body, 'Component Purpose', 'ComponentPurpose')
    if fields is not None:
        value = fields.get('component_id')
    else:
        values = [value for title, value in _claim_headings(tokens, body) if title == 'Component ID']
        if len(values) != 1:
            raise ValueError('Expected one Component Purpose ID')
        value = values[0]
    if not isinstance(value, str) or not re.fullmatch(r'C[0-9]+', value):
        raise ValueError('Invalid Component Purpose ID')
    return value
