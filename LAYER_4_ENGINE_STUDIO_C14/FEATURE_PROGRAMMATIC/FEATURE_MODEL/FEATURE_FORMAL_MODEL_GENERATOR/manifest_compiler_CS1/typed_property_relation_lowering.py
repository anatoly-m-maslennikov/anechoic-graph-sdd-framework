"""Lower typed property and relation declarations without executing authored text."""

import ast

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim

_PROPERTY_KEYS = {
    'name', 'bearer', 'classification', 'value', 'value_format', 'field_options', 'allowed_values',
    'value_cardinality', 'property_occurrence_cardinality', 'minimum_value',
    'applies_to_entity_classes', 'allowed_dependent_property', 'allowed_dependent_property_names',
    'ordered_dependent_property_pairs', 'derived_from_properties',
    'dependent_property_cardinality', 'dependent_property_value_cardinality',
    'dependent_property_value_format', 'dependent_property_name_format',
    'recursive_dependent_property_cardinality', 'recursive_dependent_property_name_format',
    'recursive_dependent_property_value_format', 'ordered_dependent_property_roles',
}
_RELATION_KEYS = {
    'name', 'source_endpoint', 'target_endpoint', 'endpoint_pairs',
    'inverse_alias', 'written_alias', 'reverse_written_alias', 'acyclic', 'derived_from',
    'forbidden_status_pairs',
}
_PROPERTY_PATHS = {
    'property.cardinality': 'property_occurrence_cardinality',
    'property.value.cardinality': 'value_cardinality',
    'property.value.format': 'value_format',
    'property.value.allowed': 'allowed_values',
    'property.value.minimum': 'minimum_value',
    'property.value.derived_from': 'derived_from_properties',
    'property.applies_to': 'applies_to_entity_classes',
    'property.classification': 'classification',
    'property.dependent_property.name.allowed': 'allowed_dependent_property_names',
    'property.dependent_property.cardinality': 'dependent_property_cardinality',
    'property.dependent_property.name.format': 'dependent_property_name_format',
    'property.dependent_property.value.cardinality': 'dependent_property_value_cardinality',
    'property.dependent_property.value.format': 'dependent_property_value_format',
    'property.dependent_property.ordered_pairs': 'ordered_dependent_property_pairs',
    'property.dependent_property.ordered_roles': 'ordered_dependent_property_roles',
    'property.dependent_property.recursive.cardinality': 'recursive_dependent_property_cardinality',
    'property.dependent_property.recursive.name.format': 'recursive_dependent_property_name_format',
    'property.dependent_property.recursive.value.format': 'recursive_dependent_property_value_format',
}
_RELATION_PATHS = {f'relation.{key}': key for key in _RELATION_KEYS - {'name'}}


def _parse_field_body(tree):
    imports = {}
    auxiliary_imports = []
    has_value_import = False
    cls = None
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module == 'anechoic.model':
            for alias in node.names:
                if alias.name == '*' or alias.asname or alias.name in imports:
                    raise ValueError('Model imports must be unique, unaliased names')
                imports[alias.name] = True
        elif (isinstance(node, ast.ImportFrom) and node.level == 0
              and node.module == 'anechoic.formal_claims'):
            for alias in node.names:
                if alias.asname or alias.name not in {'Cardinality', 'value'}:
                    raise ValueError('unsupported formal_claims import')
                if alias.name == 'value':
                    if has_value_import:
                        raise ValueError('duplicate value import')
                    has_value_import = True
                else:
                    auxiliary_imports.append(ast.ImportFrom(module=node.module, names=[alias], level=0))
        elif (isinstance(node, ast.ImportFrom) and node.level == 0
              and node.module == 'datetime'
              and all(a.name == 'datetime' and not a.asname for a in node.names)):
            auxiliary_imports.append(node)
        elif isinstance(node, ast.ClassDef) and cls is None:
            cls = node
        else:
            raise ValueError('expected Model imports and one typed field class')
    return imports, auxiliary_imports, has_value_import, cls


def _field_assignments(cls, base):
    fields = {}
    for item in cls.body:
        if not isinstance(item, ast.Assign) or len(item.targets) != 1:
            raise ValueError('typed field bodies contain only simple assignments')
        target = item.targets[0]
        key = target.id if isinstance(target, ast.Name) else None
        if isinstance(target, ast.Attribute):
            paths = _PROPERTY_PATHS if base == 'Property' else _RELATION_PATHS
            key = paths.get(ast.unparse(target))
        if key in fields or key not in (_PROPERTY_KEYS if base == 'Property' else _RELATION_KEYS):
            raise ValueError(f'duplicate or unsupported typed field: {ast.unparse(target)}')
        fields[key] = item.value
    if 'name' in fields:
        name = fields.pop('name')
        if not isinstance(name, ast.Constant) or not isinstance(name.value, str) or not name.value:
            raise ValueError('name must be a nonempty string')
    else:
        name = ast.Constant(cls.name)

    return fields, name


def _reference(node, imports, addresses):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name) or node.id not in imports or node.id not in addresses:
        raise ValueError('address references must use an imported, unambiguous Model name')
    alias = '.'.join([node.id, *reversed(parts)])
    address = addresses.get(alias)
    if not isinstance(address, str) or not address:
        raise ValueError(f'unknown or ambiguous Model reference: {alias}')
    return ast.Constant(address)


def _references(node, imports, addresses):
    if not isinstance(node, (ast.Tuple, ast.List)):
        raise ValueError('address references must be a tuple or list')  # noqa: TRY004 - invalid authored syntax
    return type(node)(elts=[_reference(item, imports, addresses) for item in node.elts], ctx=ast.Load())


def _endpoints(node, imports, addresses):
    if isinstance(node, (ast.Tuple, ast.List)):
        return type(node)(elts=[_endpoints(item, imports, addresses) for item in node.elts], ctx=ast.Load())
    if not isinstance(node, ast.Dict):
        raise ValueError('endpoints must be literal dictionaries')  # noqa: TRY004 - invalid authored syntax
    values = []
    for key, value in zip(node.keys, node.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            raise ValueError('endpoint keys must be strings')  # noqa: TRY004 - invalid authored syntax
        if key.value == 'entity_paths':
            value = _references(value, imports, addresses)
        elif key.value in {'source_endpoint', 'target_endpoint'}:
            value = _endpoints(value, imports, addresses)
        values.append(value)
    return ast.Dict(keys=node.keys, values=values)


def _lower_classification(fields, name, cls, subject, imports, addresses):
    axis = name.value
    bearer = fields.get('bearer')
    if (set(fields) != {'bearer', 'classification', 'allowed_values'}
            or not isinstance(fields['bearer'], ast.Name)
            or not isinstance(fields['classification'], ast.Constant)
            or fields['classification'].value is not True):
        raise ValueError('invalid classification axis')
    path = _reference(bearer, imports, addresses).value
    values = fields['allowed_values']
    if (not isinstance(values, ast.Tuple) or not values.elts
            or any(not isinstance(v, ast.Constant) or not isinstance(v.value, str) or not v.value.strip() for v in values.elts)
            or len({v.value for v in values.elts}) != len(values.elts)):
        raise ValueError('invalid classification axis values')
    relation_axis = (bearer.id == 'Relation' and path == 'Graph/Relation'
                     and axis == cls.name and axis in {'Transitive', 'Functional'}
                     and tuple(v.value for v in values.elts) == ('yes', 'no'))
    node_axis = bearer.id == 'Classification' and path == 'Graph/Classification'
    if (not (relation_axis or node_axis)
            or subject != f'MODEL//ANECHOIC <+ {path} >| {axis}'):
        raise ValueError('invalid classification axis scope')
    declaration = ast.Call(
        func=ast.Name(id='declare_entity', ctx=ast.Load()), args=[],
        keywords=[ast.keyword(arg='entity_name', value=ast.Constant(bearer.id)),
                  ast.keyword(arg='allowed_classification_values',
                              value=ast.Dict(keys=[ast.Constant(axis)],
                                             values=[fields['allowed_values']]))])
    output = ast.Module(body=[
        ast.ImportFrom(module='anechoic.formal_claims',
                       names=[ast.alias(name='declare_entity')], level=0),
        ast.Expr(value=declaration)], type_ignores=[])
    return ast.unparse(ast.fix_missing_locations(output)) + '\n'


def _lower_property_value(fields, has_value_import):
    if 'value' in fields:
        rule = fields.pop('value')
        if (not has_value_import or not isinstance(rule, ast.Call)
                or not isinstance(rule.func, ast.Name) or rule.func.id != 'value'
                or rule.args or len(rule.keywords) != 1
                or rule.keywords[0].arg not in {'fixed', 'default'}):
            raise ValueError('value requires imported value(fixed=...) or value(default=...)')
        choice = rule.keywords[0]
        if choice.arg == 'fixed':
            singleton = ast.Tuple(elts=[choice.value], ctx=ast.Load())
            if 'allowed_values' in fields and ast.dump(fields['allowed_values'], include_attributes=False) != ast.dump(singleton, include_attributes=False):
                raise ValueError('fixed value conflicts with allowed_values')
            fields['allowed_values'] = singleton
        else:
            options = fields.get('field_options', ast.Dict(keys=[], values=[]))
            if not isinstance(options, ast.Dict):
                raise ValueError('field_options must be a literal dictionary')
            keys = [k.value if isinstance(k, ast.Constant) else None for k in options.keys]
            if None in keys or len(keys) != len(set(keys)) or 'default_factory' in keys:
                raise ValueError('invalid or conflicting field_options')
            if 'default' in keys:
                current = options.values[keys.index('default')]
                if ast.dump(current, include_attributes=False) != ast.dump(choice.value, include_attributes=False):
                    raise ValueError('value default conflicts with field_options')
            else:
                options.keys.append(ast.Constant('default'))
                options.values.append(choice.value)
            fields['field_options'] = options


def typed_property_subject(text, addresses):
    """Derive an ordinary Property's scope from its name and bearer."""
    imports, _, _, cls = _parse_field_body(ast.parse(text))
    if cls is None:
        raise ValueError('expected one typed Property class')
    fields, name = _field_assignments(cls, 'Property')
    if 'classification' in fields or 'bearer' not in fields:
        raise ValueError('expected an ordinary Property with a bearer')
    path = _reference(fields['bearer'], imports, addresses).value
    return f'MODEL//ANECHOIC <+ {path}.{name.value}'


def declared_relation_names(records, fields):
    """Collect explicit relation names from the same Model compilation."""
    names = set()
    for _, _, claim in records:
        declaration = parse_native_model_claim(claim)
        args = declaration['arguments']
        if declaration['kind'] == 'relation' and 'derived_from' not in args:
            names.add(args['relation_name'])
    for _, _, text, kind in fields:
        if kind == 'manifest_relation':
            _, _, _, cls = _parse_field_body(ast.parse(text))
            assignments, name = _field_assignments(cls, 'Relation')
            if 'derived_from' not in assignments:
                names.add(name.value)
    return tuple(sorted(names))


def _relation_selector(node, method):
    return isinstance(node, ast.Call) and not node.args and not node.keywords and (
        isinstance(node.func, ast.Attribute) and node.func.attr == method
        and isinstance(node.func.value, ast.Name) and node.func.value.id == 'Relation'
    )


def _lower_relation_domain(fields, name, base_path, imports, addresses, relation_names):
    names = fields.get('allowed_dependent_property')
    children = fields.get('allowed_dependent_property_names')
    if names is None and isinstance(children, ast.Attribute):
        names = children
    targets = _relation_selector(fields.get('dependent_property_value_format'), 'target_references')
    if names is None and not targets:
        return
    if (not (isinstance(names, ast.Attribute) and names.attr == 'name'
             and _relation_selector(names.value, 'subclasses') and targets
             and 'Relation' in imports and relation_names)
            or ('allowed_dependent_property' in fields and children is not None)
            or name.value != 'Relations' or base_path.value != addresses.get('Atom.Header')):
        raise ValueError('Atom Relations requires both Relation selectors and a declared Relation catalog')
    fields.pop('allowed_dependent_property', None)
    fields.pop('allowed_dependent_property_names', None)
    fields['allowed_relation_names'] = ast.Tuple(
        elts=[ast.Constant(item) for item in relation_names], ctx=ast.Load())
    fields['dependent_property_value_format'] = ast.Constant('atom_reference')
    if 'value_format' not in fields:
        options = fields.get('field_options')
        optional = isinstance(options, ast.Dict) and any(
            isinstance(key, ast.Constant) and key.value == 'default'
            and isinstance(value, ast.Constant) and value.value is None
            for key, value in zip(options.keys, options.values, strict=True)
        )
        annotation = 'dict[str, list[str]] | None' if optional else 'dict[str, list[str]]'
        fields['value_format'] = ast.parse(annotation, mode='eval').body


def lower_typed_fields(kind, text, subject, addresses, *, relation_names=()):
    """Return one legacy declaration; validation remains with the static parser.

    Address-bearing fields require imported Model symbols; dotted paths require exact aliases.
    """
    if kind not in {'manifest_property', 'manifest_relation'}:
        raise ValueError(f'unsupported typed field kind: {kind}')
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        raise ValueError(f'invalid typed field: {error}') from error
    imports, auxiliary_imports, has_value_import, cls = _parse_field_body(tree)
    base = 'Property' if kind == 'manifest_property' else 'Relation'
    if (cls is None or cls.decorator_list or cls.keywords or len(cls.bases) != 1
            or not isinstance(cls.bases[0], ast.Name) or cls.bases[0].id != base
            or base not in imports):
        raise ValueError(f'expected a class with imported {base} base')
    fields, name = _field_assignments(cls, base)

    if base == 'Property' and 'classification' in fields:
        return _lower_classification(fields, name, cls, subject, imports, addresses)

    if base == 'Property':
        if 'bearer' not in fields:
            raise ValueError('property requires bearer')
        base_path = _reference(fields.pop('bearer'), imports, addresses)
        args = {'entity_name': name, 'entity_kind': ast.Constant('Property'),
                'relation_name': ast.Constant('IS_PROPERTY_OF'),
                'base_path': base_path}
        _lower_property_value(fields, has_value_import)
        _lower_relation_domain(fields, name, base_path, imports, addresses, relation_names)
        if 'applies_to_entity_classes' in fields:
            fields['applies_to_entity_classes'] = _references(fields['applies_to_entity_classes'], imports, addresses)
        function = 'declare_entity'
    else:
        args = {'relation_name': name}
        for key in ('source_endpoint', 'target_endpoint', 'endpoint_pairs'):
            if key in fields:
                fields[key] = _endpoints(fields[key], imports, addresses)
        function = 'declare_relation'
    args.update(fields)
    model_names = [ast.alias(name=n) for n in imports if n not in {'Property', 'Relation'}]
    output = [ast.ImportFrom(module='anechoic.formal_claims', names=[ast.alias(name=function)], level=0)]
    output.extend(auxiliary_imports)
    if model_names:
        output.append(ast.ImportFrom(module='anechoic.model', names=model_names, level=0))
    output.append(ast.Expr(value=ast.Call(func=ast.Name(id=function, ctx=ast.Load()), args=[],
                                         keywords=[ast.keyword(arg=k, value=v) for k, v in args.items()])))
    return ast.unparse(ast.fix_missing_locations(ast.Module(body=output, type_ignores=[]))) + '\n'
