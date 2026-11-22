"""Finite literal Role and Form declarations for lifecycle candidate checks."""
from __future__ import annotations

from dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_role_name, matches_named_value, named_value_token
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.formal_claim__pub import iter_formal_claims
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim


def compile_role_form(rows):
    declarations = []
    for row in rows:
        for block in iter_formal_claims(row['_content_bytes'].decode('utf-8')):
            declaration = parse_native_model_claim(block)
            if declaration is not None and declaration['kind'] == 'entity':
                declarations.append((row['id'], declaration))
    roles, bases = _role_classes(declarations)
    records = set()
    for source, declaration in declarations:
        args = declaration['arguments']
        qualifier = args.get('qualification_property_path')
        name = args['entity_name']
        if qualifier == 'Atom.Header.Context.Role':
            records.add(('role', name, '', source))
        elif qualifier == 'Atom.Header.Context.Form':
            if 'form_roles' in args:
                records.add(('form', name, '', source))
                records.update(('constraint', name, roles.get(role, role), source) for role in args['form_roles'])
            else:
                owner = _role_owner(declaration, roles, bases, source)
                records.add(('qualified', name, owner, source))
        elif args.get('base_path') == 'Atom.Header.Context' and name == 'Form':
            for form in args.get('allowed_values', ()):
                records.add(('form', form, '', source))
                records.update(('constraint', form, roles.get(role, role), source)
                               for role in args.get('form_roles', ()))
    return [dict(zip(('kind', 'value', 'role', 'source'), item)) for item in sorted(records)]


def _role_classes(declarations):
    roles, bases = {}, {}
    for source, declaration in declarations:
        args = declaration['arguments']
        for item in declaration.get('classes', ()):
            if item['name'] in bases:
                raise ValueError(f"{source}: duplicate Model class {item['name']}")
            bases[item['name']] = item['bases']
        if args.get('qualification_property_path') != 'Atom.Header.Context.Role':
            continue
        cls = args.get('entity_class')
        if not isinstance(cls, str) or cls in roles:
            raise ValueError(f'{source}: invalid or duplicate Role class')
        roles[cls] = args['entity_name']
    return roles, bases


def _role_owner(declaration, roles, bases, source):
    args = declaration['arguments']
    classes = [row for row in declaration['classes'] if row['name'] == args.get('entity_class')]
    if len(classes) != 1:
        raise ValueError(f'{source}: Form requires one declared Role base class')
    current, seen = classes[0]['name'], set()
    while current not in roles:
        if current in seen or len(bases.get(current, ())) != 1:
            raise ValueError(f'{source}: Form requires one declared Role base class')
        seen.add(current)
        current = bases[current][0]
    return roles[current]


@dataclass(frozen=True)
class RoleFormSchema:
    roles: frozenset[str]
    forms: frozenset[str]
    qualified: frozenset[tuple[str, str]]
    constraints: tuple[tuple[str, frozenset[str]], ...]

    def names(self, field):
        if field == 'role':
            return self.roles
        return self.forms | {form for _, form in self.qualified}

    def decode(self, field, carried):
        if field == 'role':
            carried = canonical_role_name(carried)
        matches = {name for name in self.names(field) if matches_named_value(carried, name)}
        if len(matches) > 1:
            raise ValueError(f'Ambiguous {field} Carrier spelling.')
        return next(iter(matches), carried)

    def encode(self, field, canonical):
        if not isinstance(canonical, str) or canonical not in self.names(field):
            return canonical
        token = named_value_token(canonical)
        if token is None:
            return canonical
        if self.decode(field, token) != canonical:
            raise ValueError(f'Ambiguous {field} Carrier spelling.')
        return token

    def validate(self, role, form):
        if role not in self.roles:
            raise ValueError(f'Role is not declared: {role}')
        qualified_roles = {declared_role for declared_role, declared_form in self.qualified if declared_form == form}
        if qualified_roles and form not in self.forms and role not in qualified_roles:
            raise ValueError(f'Role {role} is not permitted for Form {form}; allowed: {", ".join(sorted(qualified_roles))}')
        for constrained_form, allowed in self.constraints:
            if form == constrained_form and role not in allowed:
                raise ValueError(f'Role {role} is not permitted for Form {form}; allowed: {", ".join(sorted(allowed))}')


def load_role_form(records, source_ids):
    if not isinstance(records, list):
        raise ValueError('invalid Role/Form records')
    seen = set()
    roles, forms, qualified, constraints = set(), set(), set(), {}
    for row in records:
        if not isinstance(row, dict) or set(row) != {'kind', 'value', 'role', 'source'}:
            raise ValueError('invalid Role/Form record')
        kind, value, role, source = (row[k] for k in ('kind', 'value', 'role', 'source'))
        if (kind not in {'role', 'form', 'qualified', 'constraint'} or not isinstance(value, str) or not value
                or not isinstance(role, str) or not isinstance(source, str) or source not in source_ids
                or (kind in {'role', 'form'} and role) or (kind in {'qualified', 'constraint'} and not role)):
            raise ValueError('invalid Role/Form record')
        key = (kind, value, role, source)
        if key in seen:
            raise ValueError('duplicate Role/Form record')
        seen.add(key)
        if kind == 'role':
            roles.add(value)
        elif kind == 'form':
            forms.add(value)
        elif kind == 'qualified':
            qualified.add((role, value))
        else:
            constraints.setdefault((value, source), set()).add(role)
    return RoleFormSchema(frozenset(roles), frozenset(forms), frozenset(qualified),
                          tuple((form, frozenset(allowed)) for (form, _), allowed in sorted(constraints.items())))
