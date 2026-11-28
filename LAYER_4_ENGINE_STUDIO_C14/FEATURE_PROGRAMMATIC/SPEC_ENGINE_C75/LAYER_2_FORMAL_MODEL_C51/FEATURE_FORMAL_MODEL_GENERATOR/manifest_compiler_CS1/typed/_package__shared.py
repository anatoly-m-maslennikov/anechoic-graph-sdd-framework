"""Typed Model lowering interfaces."""

from ._typed_field_syntax import _endpoints as _endpoints, _field_assignments as _field_assignments, _parse_field_body as _parse_field_body, _reference as _reference, _references as _references
from ._typed_property_rules import _lower_axis as _lower_axis, _lower_property_value as _lower_property_value
from .typed_addresses import typed_addresses as typed_addresses
from .typed_node_lowering import _model_record as _model_record, lower_typed_node as lower_typed_node
