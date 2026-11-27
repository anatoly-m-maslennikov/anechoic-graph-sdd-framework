"""Publish a configured Realization Graph against its admitted native base."""

import json

from .accepted_model import generation_rows
from .generation import GenerationBaseChanged, _HEX, _native_graph_payload, _unique, _write_reuse
from .realization_projection import has_table, replace, restore_property_graph
from .table_names import sync_query_views


def replace_pending_graph(connection, data):
    """Publish a graph against the exact admitted native generation."""
    if "force_graph" in data and data["force_graph"] is not True:
        raise ValueError("Invalid graph force flag")
    connection.execute("BEGIN TRANSACTION")
    dropped = False
    try:
        rows = generation_rows(connection)
        if (len(rows) != 1 or rows[0][0] != data["base_generation"]
                or not has_table(connection, "native_graph", "int_labels")
                or not has_table(connection, "main", "mrt_atom_graph_relations")):
            raise GenerationBaseChanged("Generation base changed or is not native")
        base, model, structure = rows[0]
        witness_rows = connection.execute("SELECT witness FROM ops_generation_reuse").fetchall()
        if len(witness_rows) != 1:
            raise GenerationBaseChanged("Graph witness is unavailable")
        previous = json.loads(witness_rows[0][0])
        witness = data["reuse"]
        old_graph = previous.get("inputs", {}).get("graph")
        if (not isinstance(witness, dict) or not isinstance(witness.get("inputs"), dict)
                or not isinstance(old_graph, str)
                or (old_graph != "pending" and _HEX.fullmatch(old_graph) is None)
                or (old_graph == witness["inputs"].get("graph") and not data.get("force_graph"))
                or witness["inputs"].get("graph") in (None, "pending", "disabled")
                or {**previous, "inputs": {**previous["inputs"], "graph": witness["inputs"]["graph"]}} != witness):
            raise GenerationBaseChanged("Graph witness changed or is disabled")
        components = {"C00", *json.loads(structure, object_pairs_hook=_unique)["components"]}
        graph = _native_graph_payload(data, components, {})
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        dropped = True
        replace(connection, graph, components)
        _write_reuse(connection, data, model)
        sync_query_views(connection)
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        if dropped:
            restore_property_graph(connection)
        raise
    return base
