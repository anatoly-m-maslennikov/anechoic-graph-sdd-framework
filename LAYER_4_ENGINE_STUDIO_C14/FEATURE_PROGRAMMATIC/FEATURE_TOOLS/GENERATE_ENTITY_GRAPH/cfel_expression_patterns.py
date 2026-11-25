"""Patterns for the bounded CFEL expression inventory."""

import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_constraint_common import _COUNT

_PROPERTY = re.compile(
    rf"^(?P<property>.+?)(?P<descendants>\.\*\*|\.\*)?"
    rf"(?:\[(?P<name_format>[^\]]*)\])?"
    rf"\{{::?{_COUNT}\}}"
    rf"(?:\s*::?\s*(?:\[(?P<value_format>[^\]]*)\])?\{{::?(?P<value_minimum>0|[1-9][0-9]*)(?P<value_tail>\+|\.\.(?P<value_maximum>0|[1-9][0-9]*))?\}})?$"
)
_PROPERTY_VALUE = re.compile(
    rf"^(?P<property>.+?)(?P<descendants>\.\*\*|\.\*)?\s*::?\s*(?:\[(?P<value_format>[^\]]*)\])?"
    rf"(?:\{{::?{_COUNT}\}})?$"
)
_NAMED_PROPERTY = re.compile(rf"^(?P<property>.+?)(?:\{{::?{_COUNT}\}})?\s*::?$")
_RELATION = re.compile(
    rf"^(?P<source>.+?)\s*(?:\{{::?(?P<forward_minimum>0|[1-9][0-9]*)(?P<forward_tail>\+|\.\.(?P<forward_maximum>0|[1-9][0-9]*))?\}}\s*)?"
    rf"(?:<\(\((?P<reverse_relation>[^()]+)\)\)|\(\((?P<relation>[^()]+)\)\)|(?P<relation_notation>\+>|<\+))\s*"
    rf"(?:\{{::?(?P<reverse_minimum>0|[1-9][0-9]*)(?P<reverse_tail>\+|\.\.(?P<reverse_maximum>0|[1-9][0-9]*))?\}}\s*)?"
    rf"(?P<target>.+)$"
)
_GROUPED_INSTANCE_RELATION = re.compile(
    r"^\((?P<source>[^()]+)\)\s*\(\(IS_INSTANCE_OF\)\)\s*(?P<target>[^()]+)$"
)
_RELATION_WITHOUT_TARGET = re.compile(
    rf"^(?P<source>.+?)\s*\{{:(?P<forward_minimum>0|[1-9][0-9]*)(?P<forward_tail>\+|\.\.(?P<forward_maximum>0|[1-9][0-9]*))?\}}\s*"
    rf"(?:\(\((?P<relation>[^()]+)\)\)|(?P<relation_notation>\+>|<\+)|(?P<bare_relation>[A-Z][A-Z0-9_]*))$"
)
_ALLOWED_CLASSIFICATION_VALUE = re.compile(
    r"^(?P<subject>[A-Za-z_][A-Za-z_0-9 .-]*)\s*>\|\s*(?P<axis>[A-Za-z_][A-Za-z_0-9 .-]*?):\s*(?P<value>[A-Za-z_][A-Za-z_0-9 .-]*)$"
)
_FORWARD_CLASSIFICATION = re.compile(
    r"^(?P<subject>.+?)\s*>\|\s*(?P<axis>.+?)\s*(?P<operator>==|=)\s*(?P<value>.+)$"
)
_REVERSE_CLASSIFICATION = re.compile(
    r"^(?P<axis>.+?)\s*\|<\s*(?P<subject>.+?)\s*(?P<operator>==|=)\s*(?P<value>.+)$"
)
_FORWARD_GROUPED_CLASSIFICATION = re.compile(
    r"^(?P<subject>.+?)\s*>\|\s*\(\s*(?P<axis>.+?)\s*(?P<operator>==|=)\s*(?P<value>.+?)\s*\)$"
)
_REVERSE_GROUPED_CLASSIFICATION = re.compile(
    r"^\(\s*(?P<axis>.+?)\s*(?P<operator>==|=)\s*(?P<value>.+?)\s*\)\s*\|<\s*(?P<subject>.+)$"
)
_ALLOWED_LITERAL = re.compile(r"^(?P<property>.+?)\s*:{1,2}\s*(?P<literal>[^\[\]{}]+)$")
_QUALIFIED_ALLOWED_LITERAL = re.compile(r"^(?P<property>.+\).+?)\s*:{1,2}\s*(?P<literal>[^\[\]{}]+)$")
_PROPERTY_MINIMUM = re.compile(r"^(?P<property>.+?)\s*>=\s*(?P<value>-?\d+(?:\.\d+)?)$")
_RELATION_ALIAS = re.compile(r'^alias\(\s*(?:Relation//)?(?P<name>[A-Za-z][A-Za-z0-9_]*)\s*\)\s*==\s*"(?P<glyph>[^"\r\n]+)"$')
_OPERATOR_SYMBOL = re.compile(r'Operator//(?P<name>[A-Za-z_][A-Za-z_0-9]*)\s*==\s*(?P<symbol>"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*")')
_COUNTERPART = re.compile(r'^(?P<source>Relation//[A-Za-z][A-Za-z0-9_]*)\s*<-->\s*(?P<target>Relation//[A-Za-z][A-Za-z0-9_]*)$')
_UNFILTERED_UNIQUE = re.compile(r"^UNIQUE\(\s*(?P<population>[A-Za-z][A-Za-z0-9_ /.-]*)//\$[A-Za-z][A-Za-z0-9_]*\s*,\s*\(\s*\.(?P<key>[A-Za-z_][A-Za-z_0-9 .-]*)\s*\)\s*\)$")
_INSTANCE_BINDING = re.compile(r'^(?P<kind>[A-Za-z][A-Za-z0-9_ /.-]*)//\$(?P<variable>[A-Za-z][A-Za-z0-9_]*)$')
_SCOPED_INSTANCE_BINDING = re.compile(r'^(?P<kind>.+)//\$(?P<variable>[A-Za-z][A-Za-z0-9_]*)$')
_INSTANCE_POPULATION = re.compile(rf'^(?P<kind>[A-Za-z][A-Za-z0-9_ /.-]*)//\$(?P<variable>[A-Za-z][A-Za-z0-9_]*)\{{:{_COUNT}\}}$')
_PROPERTY_INSTANCE_POPULATION = re.compile(rf'^(?P<bearer>[A-Za-z][A-Za-z0-9_ /.-]*)\.\*\*//\{{:{_COUNT}\}}$')
_MODEL_BINDING = re.compile(r'^IF\s+\$(?P<variable>[A-Za-z][A-Za-z0-9_]*)\s+in\s*\((?P<selection>[^()]*)\)\s+THEN\s*\(', re.I)
