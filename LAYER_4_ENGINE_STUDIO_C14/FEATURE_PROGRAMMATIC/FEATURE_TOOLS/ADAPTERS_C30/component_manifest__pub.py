"""Read native Component claims without executing authored code."""

from markdown_it import MarkdownIt

from .native_model_claim__pub import parse_native_model_claim
from .formal_claim__pub import formal_claim


def _formal_component_instance(source):
    claim = parse_native_model_claim(source)
    args = claim['arguments'] if claim and claim['kind'] == 'entity' else {}
    instance = args.get('instance', {})
    if (set(args) != {'entity_name', 'instance'} or args['entity_name'] != 'Component Manifest'
            or instance.get('type') != 'ComponentManifest'):
        raise ValueError('Expected one formal ComponentManifest instance')
    return instance['fields']


def parse_component_manifest(body):
    tokens = MarkdownIt('commonmark').parse(body)
    headings = {}
    for i, token in enumerate(tokens):
        if token.type != 'heading_open':
            continue
        title = tokens[i + 1].content.strip().casefold()
        if title in {'purpose', 'formal manifest'}:
            if title == 'purpose' and (token.tag != 'h2' or token.level != 0):
                continue
            if token.tag != 'h2' or token.level != 0 or title in headings:
                raise ValueError('Expected unique top-level Component Manifest headings')
            headings[title] = i
    lines = body.splitlines()

    def section_end(index):
        return next((t.map[0] for t in tokens[index + 1:]
                     if t.type == 'heading_open' and t.tag in {'h1', 'h2'} and t.level == 0), len(lines))

    purpose_index = headings.get('purpose')
    purpose = ('\n'.join(lines[tokens[purpose_index].map[1]:section_end(purpose_index)]).strip() or None
               if purpose_index is not None else None)
    formal_index = headings.get('formal manifest')
    if formal_index is not None:
        if any(t.type == 'heading_open' and t.tag == 'h2' and t.level == 0
               and tokens[i + 1].content.strip().casefold() == 'claim'
               for i, t in enumerate(tokens)):
            raise ValueError('Ambiguous Component Manifest formal sections')
        end = section_end(formal_index)
        section = [t for t in tokens[formal_index + 1:] if t.map and t.map[0] < end]
        fences = [t for t in section if t.type == 'fence']
        if (len(fences) != 1 or fences[0].info.strip().casefold() != 'python'
                or fences[0].level != 0 or any(t.type == 'heading_open' for t in section)):
            raise ValueError('Expected one Python Formal Manifest')
        return _formal_component_instance(fences[0].content), purpose
    return _formal_component_instance(formal_claim(body)), purpose


def parse_component_manifest_fields(body):
    return parse_component_manifest(body)[0]
