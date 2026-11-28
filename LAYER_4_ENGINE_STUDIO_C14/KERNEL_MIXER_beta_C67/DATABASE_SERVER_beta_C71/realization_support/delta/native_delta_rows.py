"""Write the addressed native delta rows."""

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native__shared import write_staged_atoms
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.native_delta_validation import _stage


def _write_atoms(connection):
    connection.execute(
        (
            "DELETE FROM main.mrt_atoms WHERE (relative_path, filename) IN (S"
            "ELECT * FROM int_delta_paths)"
        )
    )
    connection.execute(
        (
            "DELETE FROM main.mrt_atom_references WHERE (relative_path, filen"
            "ame) IN (SELECT * FROM int_delta_paths)"
        )
    )
    write_staged_atoms(connection)


def _write_relations(connection, new_edges):
    connection.execute("""DELETE FROM main.mrt_atom_graph_relations WHERE
        (NOT derived AND source_kind = 'Atom' AND source_ref IN (SELECT
            reference FROM int_delta_old)) OR
        (derived AND target_kind = 'Atom' AND target_ref IN (SELECT reference
            FROM int_delta_old))""")
    connection.execute(
        (
            "CREATE TEMP TABLE int_delta_new_edges AS SELECT * FROM main.mrt_"
            "atom_graph_relations WHERE false"
        )
    )
    _stage(connection, "int_delta_new_edges", new_edges, 6)
    connection.execute(
        (
            "INSERT INTO main.mrt_atom_graph_relations SELECT * FROM int_delt"
            "a_new_edges"
        )
    )


def _prune_vertices(connection, components):
    connection.execute("CREATE TEMP TABLE int_delta_components (ref VARCHAR)")
    _stage(
        connection, "int_delta_components", [(ref,) for ref in components], 1
    )
    connection.execute("""DELETE FROM native_graph.int_reference v WHERE EXISTS
        (SELECT 1 FROM int_delta_vertices d WHERE d.kind = v.kind AND d.ref =
            v.ref)
        AND NOT (v.kind = 'Component' AND v.ref IN (SELECT ref FROM
            int_delta_components))
        AND NOT EXISTS (SELECT 1 FROM main.mrt_atom_references n WHERE v.kind =
            'Atom' AND n.reference = v.ref)
        AND NOT EXISTS (SELECT 1 FROM main.mrt_atom_graph_relations r WHERE
            (r.source_kind = v.kind AND r.source_ref = v.ref)
                        OR (r.target_kind = v.kind AND r.target_ref =
                            v.ref))""")
