"""Native query template and result behavior cases."""

from ..group_2._native_query_behavior_ticket import TicketCases
from ..group_2._native_query_behavior_query import QueryCases
from ..group_2._native_query_behavior_inventory import InventoryCases
from ._native_query_behavior_tree import TreeCases
from ..group_2._native_query_behavior_component import ComponentCases


class NativeQueryBehaviorCases(
    TicketCases, QueryCases, InventoryCases, TreeCases, ComponentCases
):
    pass
