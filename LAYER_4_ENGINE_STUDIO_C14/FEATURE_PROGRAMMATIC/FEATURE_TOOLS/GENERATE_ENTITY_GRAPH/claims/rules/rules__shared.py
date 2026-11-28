"""Native Claim rule projection."""

from ._native_claim_entity_rules import (
    _native_entity as _native_entity,
    _native_entity_dependents as _native_entity_dependents,
    _native_entity_population as _native_entity_population,
)
from ._native_claim_property_rules import (
    _native_property as _native_property,
    _native_property_dependents as _native_property_dependents,
    _native_property_scalar as _native_property_scalar,
)
from ._native_claim_property_ext import (
    _native_property_fallbacks as _native_property_fallbacks,
    _native_property_rules as _native_property_rules,
)
from ._native_claim_relation_rules import _native_relation as _native_relation
