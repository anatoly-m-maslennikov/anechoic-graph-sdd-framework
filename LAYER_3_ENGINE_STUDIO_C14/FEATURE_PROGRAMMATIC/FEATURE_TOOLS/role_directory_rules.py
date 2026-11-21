
"""Compile explicit Role ordering claims into canonical directory names."""
import re

from carrier_aliases import canonical_role_name, named_value_token

_ORDER = re.compile(
    r'^Atom/\(\s*\.Header\.Context\.Role\s*:=\s*(?P<role>"[^"\r\n]+"|[A-Za-z][A-Za-z0-9 _-]*)\s*\)'
    r'\s*>\|\s*\(\s*Role Order Number\s*==\s*(?P<order>[1-9][0-9]*)\s*\)$'
)


def compile_role_folders(statements):
    """Return canonical Role -> (derived folder, source) for bounded order claims."""
    return role_folders_from_orders(_legacy_role_orders(statements))


def _legacy_role_orders(statements):
    for statement, provenance in statements:
        if 'Role Order Number' not in statement:
            continue
        match = _ORDER.fullmatch(statement)
        if match is None:
            raise ValueError(f'{provenance}: unsupported Role Order Number declaration')
        role = match['role'].strip()
        if role.startswith('"'):
            role = role[1:-1]
        yield role, int(match['order']), provenance


def role_folders_from_orders(records):
    result, orders, tokens = {}, set(), set()
    for role, order, provenance in records:
        role = canonical_role_name(role)
        token = named_value_token(role)
        if (type(order) is not int or order < 1 or token is None
                or role in result or token in tokens or order in orders):
            raise ValueError(f'{provenance}: duplicate or invalid Role order binding')
        result[role] = (f'{order:02d}_{token}', provenance)
        orders.add(order)
        tokens.add(token)
    return result
