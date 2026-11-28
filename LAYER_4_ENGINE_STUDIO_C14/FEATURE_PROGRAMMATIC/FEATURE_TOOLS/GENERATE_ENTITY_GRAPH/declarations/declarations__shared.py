"""Declaration evidence, authority and catalogue interface."""

from .declaration_evidence import (
    Record as Record,
    _active_source_matches_metadata as _active_source_matches_metadata,
    _single_valid_governed_subject as _single_valid_governed_subject,
    _source as _source,
    _source_with_matching_bytes as _source_with_matching_bytes,
    _subjects as _subjects,
    _view as _view,
)
from .declaration_relations import (
    _add_relation_candidate as _add_relation_candidate,
    resolve_relation_authorities as resolve_relation_authorities,
)
from .declaration_sources import (
    compose_declaration_catalog as compose_declaration_catalog,
)
