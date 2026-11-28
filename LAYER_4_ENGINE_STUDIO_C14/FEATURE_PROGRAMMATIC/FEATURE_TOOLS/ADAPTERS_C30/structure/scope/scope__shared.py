"""Entry points for this Adapter package."""

from .scope_carrier__pub import (
    DELEGATION_ROLE_FOLDERS as DELEGATION_ROLE_FOLDERS,
    ScopeDeclarationError as ScopeDeclarationError,
    has_projection_marker as has_projection_marker,
    has_scope_declaration_form as has_scope_declaration_form,
)
from .scope_declaration_parse__pub import (
    parse_scope_unit_declaration as parse_scope_unit_declaration,
)
from .scope_declaration_tree import (
    ScopeUnitDeclaration as ScopeUnitDeclaration,
    ScopeUnitDeclarations as ScopeUnitDeclarations,
)
