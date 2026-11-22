
"""Resolve the effective Container of the selected root Project Declaration."""
from hashlib import sha256

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import header_value, project_root_container_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_carrier__pub import ScopeDeclarationError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_declaration_parse__pub import ScopeUnitDeclaration, parse_scope_unit_declaration


def effective_root_container_header(
    metadata, *, path, raw, root_declaration_path, root_declaration_pin,
):
    """Return a validation Header without changing the stored carrier metadata."""
    if path != root_declaration_path or root_declaration_pin is None or header_value(metadata, 'container')[0]:
        return metadata
    if sha256(raw).hexdigest() != root_declaration_pin['sha256']:
        return metadata
    try:
        declaration = parse_scope_unit_declaration(raw, path)
    except ScopeDeclarationError:
        return metadata
    if (not isinstance(declaration, ScopeUnitDeclaration) or not declaration.is_root
            or declaration.atom_id != root_declaration_pin['atom_id']
            or declaration.version != root_declaration_pin['version']):
        return metadata

    return project_root_container_view(metadata)
