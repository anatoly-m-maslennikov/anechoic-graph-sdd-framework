"""Add available import and test projections to the property graph."""

from typing import Any


def add_import_projection(
    connection: Any, vertices: list[str], edges: list[str]
) -> None:
    if connection.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_catalog = current_database() "
        "AND table_schema = 'main' AND table_name = 'import_nodes'"
    ).fetchone()[0]:
        vertices.append("main.import_nodes LABEL ImportNode")
        edges.append(
            "main.import_edges SOURCE KEY(source_key) "
            "REFERENCES main.import_nodes(node_key) "
            "DESTINATION KEY(target_key) "
            "REFERENCES main.import_nodes(node_key) LABEL Imports"
        )
        _add_test_edges(connection, edges)


def _add_test_edges(connection, edges):
    if connection.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_catalog = current_database() "
        "AND table_schema = 'realization_internal' "
        "AND table_name = 'package_tests'"
    ).fetchone()[0]:
        for table, label in (
            ("package_tests", "TESTS"),
            ("package_tested_by", "IS_TESTED_BY"),
        ):
            edges.append(
                f"realization_internal.{table} SOURCE KEY(source_key) "
                "REFERENCES main.import_nodes(node_key) "
                "DESTINATION KEY(target_key) "
                f"REFERENCES main.import_nodes(node_key) LABEL {label}"
            )
        edges.extend(
            (
                "realization_internal.component_tests SOURCE KEY(source_key) "
                "REFERENCES main.import_nodes(node_key) "
                "DESTINATION KEY(target_kind, target_key) "
                "REFERENCES internal.reference(kind, ref) "
                "LABEL TESTS_COMPONENT",
                "realization_internal.component_tested_by "
                "SOURCE KEY(source_kind, source_key) "
                "REFERENCES internal.reference(kind, ref) "
                "DESTINATION KEY(target_key) "
                "REFERENCES main.import_nodes(node_key) "
                "LABEL COMPONENT_IS_TESTED_BY",
            )
        )
    else:
        _add_legacy_test_edges(connection, edges)


def _add_legacy_test_edges(connection, edges):
    for table, label in (
        ("test_edges", "TESTS"),
        ("tested_by_edges", "IS_TESTED_BY"),
    ):
        if connection.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_catalog = current_database() "
            "AND table_schema = 'main' AND table_name = ?",
            [table],
        ).fetchone()[0]:
            edges.append(
                f"main.{table} SOURCE KEY(source_key) "
                "REFERENCES main.import_nodes(node_key) "
                "DESTINATION KEY(target_key) "
                f"REFERENCES main.import_nodes(node_key) LABEL {label}"
            )
