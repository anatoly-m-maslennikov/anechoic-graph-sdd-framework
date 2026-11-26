"""Lower typed node value rules to existing static model declarations."""

import re

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_property_fields import (
    _field_name,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    model_class_target,
    parse_native_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.typed_manifest_node import (
    parse_typed_manifest_node,
)


def _lower_node_values(node, roots, parents, properties, root, display, claims):
    ancestors, pending = set(), list(node['bases'])
    while pending:
        current = pending.pop()
        if current in ancestors:
            continue
        ancestors.add(current)
        pending.extend(parents.get(current, ()))
    for name, (mode, value) in node['values'].items():
        if name == 'container_type':
            if mode != 'fixed' or not isinstance(value, tuple) or value[0] != 'type' or value[1] not in roots:
                raise ValueError('container_type requires a known fixed Model class')
            claims.append((root + '.Constraints', f"from anechoic.formal_claims import declare_entity\nfrom anechoic.model import {node['name']}\ndeclare_entity(entity_name={display + ' Constraints'!r}, constraints_for={root!r}, instance_relation_constraints={{'IS_CONTAINED_BY': {{'target_entity_paths': ({roots[value[1]]!r},), 'targets_per_source': 1}}}})\n"))
            continue
        if isinstance(value, tuple):
            raise ValueError(f'{name}: type references are not scalar values')  # noqa: TRY004
        matches = [args for args in properties if _field_name(args['entity_name']) == name
                   and args['base_path'].partition('.')[0] in {roots.get(base) for base in ancestors}]
        if len(matches) != 1:
            raise ValueError(f'{name}: missing or ambiguous inherited Property')
        prop = matches[0]
        keys = ('value_cardinality', 'property_occurrence_cardinality')
        options = dict(prop.get('field_options', {}))
        if mode == 'default' or 'default' in options or 'default_factory' in options:
            options.pop('default_factory', None)
            options['default'] = value
        fields = {key: prop[key] for key in keys if key in prop}
        if mode == 'fixed':
            fields.update(allowed_values=(value,), value_cardinality=1, property_occurrence_cardinality=1)
        if 'default' in options:
            fields['property_occurrence_cardinality'] = {'minimum': 0, 'maximum': 1}
        fields.update(field_options=options, applies_to_entity_classes=(root,))
        args = ', '.join(f'{key}={item!r}' for key, item in fields.items())
        suffix = prop['base_path'].partition('.')[2]
        subject = root + ('.' + suffix if suffix else '') + '.' + prop['entity_name']
        claims.append((subject, f"from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name={prop['entity_name']!r}, entity_kind='Property', relation_name='IS_PROPERTY_OF', base_path={prop['base_path']!r}, value_format={prop['value_format']}, {args})\n"))


def lower_typed_node(text, records, subject=None):
    node = parse_typed_manifest_node(text)
    roots, parents, properties = {}, {}, []
    for _, declared_subject, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration['arguments']
        if name := args.get('entity_class'):
            root = model_class_target(declared_subject, args['entity_name'])
            if name in roots:
                raise ValueError(f'ambiguous Model class: {name}')
            roots[name] = root
            parents[name] = next(item['bases'] for item in declaration['classes'] if item['name'] == name)
        if args.get('entity_kind') == 'Property' and 'applies_to_entity_classes' not in args:
            properties.append(args)
    if any(base not in roots or not roots[base] for base in node['bases']):
        raise ValueError("unknown typed node base")
    if len(node['bases']) > 1 and subject is None:
        raise ValueError("multiple node bases require an explicit Model scope")
    root = (subject.split(' <+ ', 1)[1] if subject else
            (roots[node['bases'][0]] + '//' if node['bases'] else '') + node['name'])
    display = re.split(r'/+', root)[-1]
    if '.' in display:
        raise ValueError('typed node scope must identify a Model class')
    bases = ', '.join(node['bases'])
    imports = f"from anechoic.model import {bases}\n" if bases else ''
    signature = f"({bases})" if bases else ''
    identity = f", identity_properties=({node['identity']!r},)" if node['identity'] else ''
    classifications = f", classifications={node['classifications']!r}" if node['classifications'] else ''
    claims = [(root, f"from anechoic.formal_claims import declare_entity\n{imports}class {node['name']}{signature}:\n    pass\ndeclare_entity(entity_name={display!r}, entity_class={node['name']}, entity_kind='Primary'{identity}{classifications})\n")]
    _lower_node_values(node, roots, parents, properties, root, display, claims)
    return [('MODEL//ANECHOIC <+ ' + subject, claim) for subject, claim in claims]
