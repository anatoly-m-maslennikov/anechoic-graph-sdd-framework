"""Keep native Reference vertices and relation edges alongside the admitted rows."""


def replace_native_graph(connection, relation_types, components):
    connection.execute("DROP SCHEMA IF EXISTS native_graph CASCADE")
    connection.execute("CREATE SCHEMA native_graph")
    connection.execute("CREATE TABLE native_graph.int_reference (kind VARCHAR, ref VARCHAR, PRIMARY KEY (kind, ref))")
    connection.execute(
        "INSERT INTO native_graph.int_reference SELECT 'Atom', reference FROM main.mrt_atom_references "
        "UNION SELECT 'Component', unnest(?::VARCHAR[]) "
        "UNION SELECT source_kind, source_ref FROM main.mrt_atom_graph_relations "
        "UNION SELECT target_kind, target_ref FROM main.mrt_atom_graph_relations", [sorted(components)],
    )
    connection.execute("CREATE TABLE native_graph.int_labels (ordinal INTEGER PRIMARY KEY, name VARCHAR NOT NULL)")
    if relation_types:
        connection.executemany("INSERT INTO native_graph.int_labels VALUES (?, ?)", list(enumerate(relation_types)))
    for index, label in enumerate(relation_types):
        connection.execute(
            f"CREATE TABLE native_graph.int_relation_{index} AS "
            "SELECT DISTINCT source_kind, source_ref, target_kind, target_ref, derived "
            "FROM main.mrt_atom_graph_relations WHERE relation_type = ?", [label],
        )


def native_edges(connection, reference, realization=False):
    edges = []
    for index, label in connection.execute("SELECT ordinal, name FROM native_graph.int_labels ORDER BY ordinal").fetchall():
        if realization and label.casefold() == "imports":
            if connection.execute(f"SELECT 1 FROM native_graph.int_relation_{int(index)} LIMIT 1").fetchone():
                raise ValueError("Native IMPORTS relations conflict with realization Imports graph label")
            continue
        quoted = '"' + label.replace('"', '""') + '"'
        edges.append(f"native_graph.int_relation_{int(index)} SOURCE KEY(source_kind, source_ref) REFERENCES {reference}(kind, ref) "
                     f"DESTINATION KEY(target_kind, target_ref) REFERENCES {reference}(kind, ref) LABEL {quoted}")
    return edges
