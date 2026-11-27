"""Canonical Beta database names and compatibility for existing SQL."""

import re

from . import analysis_projection, flows, realization_projection


ATOM_FAMILY_VIEWS = {
    "mrt_spec_atoms": ("S",),
    "mrt_ticket_atoms": ("T",),
    "mrt_project_config_atoms": ("P", "C"),
}
_REAL_GRAPH_NAMES = {
    **{name: f"mrt_real_graph_{name}" for name in (
        "import_nodes", "import_edges", "package_imports", "package_external_imports",
        "code_units", "code_unit_calls", "test_edges", "tested_by_edges",
    )},
    "module_imports": "mrt_real_graph_import_occurrences",
    "architecture_package_bindings": "mrt_real_graph_package_spec_bindings",
}
_DIAG_NAMES = {
    "import_read_issues": "mrt_diag_import_read_issues",
    "import_cycles": "mrt_diag_import_cycles",
    "antipattern_findings": "mrt_diag_antipatterns",
    "code_access_findings": "mrt_diag_code_access",
    "state_effect_findings": "mrt_diag_state_effects",
}
_ATOM_AND_FLOW_NAMES = {
    "native_references": "mrt_atom_references",
    "relations": "mrt_atom_graph_relations",
    "component_flows": "mrt_flow_actions",
}
_DOMAIN_NAMES = _REAL_GRAPH_NAMES | _DIAG_NAMES | _ATOM_AND_FLOW_NAMES
DOMAIN_COMPATIBILITY = {f"mrt_{old}": new for old, new in _DOMAIN_NAMES.items()}
PUBLIC_NAMES = {
    "project_structure": "mrt_project_structure",
    "model_entities": "mrt_model_entities",
    "model_properties": "mrt_model_properties",
    "model_tree": "mrt_model_tree",
    "model_primary_entities": "mrt_model_primary_entities",
    "diag_model_manifests": "mrt_diag_model_manifests",
    **{name: f"mrt_{name}" for name in ("atoms", "flow_overlap_candidates", "flow_similar_actions")},
    **_DOMAIN_NAMES,
    **{name: f"biz_{name}" for name in (
        "package_coupling", "architecture_code_metrics", "architecture_spec_metrics", "architecture_ratios",
        "package_review_profiles", "package_largest_files",
    )},
    "flow_events": "src_flow_events",
    "work_journal": "ops_work_journal",
    "query_log": "ops_query_log",
}
_MAIN_NAMES = {old: new for old, new in PUBLIC_NAMES.items() if not new.startswith("ops_")} | {
    "project_binding": "ops_project_binding",
    "generation": "ops_generation",
    "generation_reuse": "ops_generation_reuse",
    "lifecycle_lenses": "int_lifecycle_lenses",
}
_ALIASES = {
    **{old: new for old, new in _MAIN_NAMES.items() if old in PUBLIC_NAMES},
    **DOMAIN_COMPATIBILITY,
    "generation": "ops_generation",
    "int_lifecycle_generation": "ops_generation",
    "lifecycle_lenses": "int_lifecycle_lenses",
}
_REALIZATION_WORK = {
    "component_reference", "package_tests", "package_tested_by", "component_tests",
    "component_tested_by", "source_antipatterns",
}


def main_objects(connection):
    return dict(connection.execute(
        "SELECT table_name, table_type FROM information_schema.tables "
        "WHERE table_catalog = current_database() AND table_schema = 'main'"
    ).fetchall())


def sync_query_views(connection):
    objects = main_objects(connection)
    for name, families in ATOM_FAMILY_VIEWS.items():
        choices = ", ".join(repr(family) for family in families)
        connection.execute(f"CREATE OR REPLACE VIEW main.{name} AS SELECT * FROM main.mrt_atoms "
                           f"WHERE split_part(reference, '-', 2) IN ({choices})")
    for old, new in _ALIASES.items():
        if new in objects:
            columns = "*, axes AS classifications" if old == "model_primary_entities" else "*"
            connection.execute(f"CREATE OR REPLACE VIEW main.{old} AS SELECT {columns} FROM main.{new}")
        elif objects.get(old) == "VIEW":
            connection.execute(f"DROP VIEW main.{old}")


def migrate_legacy_names(connection, objects, *, legacy):
    """Rename retained rows and regenerate their derived views in the caller's transaction."""
    names = _MAIN_NAMES if legacy else {old: new for old, new in DOMAIN_COMPATIBILITY.items()
                                        if new not in objects}
    if not any(old in objects for old in names):
        return False
    for old, new in names.items():
        kind = objects.get(old)
        if kind is not None:
            _move_projection(connection, old, new, kind)
    if legacy:
        _migrate_graph_tables(connection)
    if {"import_nodes", "mrt_import_nodes", "mrt_real_graph_import_nodes"} & objects.keys():
        realization_projection.prepare(connection)
    if {"architecture_code_metrics", "biz_architecture_code_metrics"} & objects.keys():
        analysis_projection.prepare(connection)
    if {"flow_events", "src_flow_events"} & objects.keys():
        flows.initialize_flows(connection)
    return True


def _move_projection(connection, old, new, kind):
    if kind == "BASE TABLE":
        connection.execute(f"ALTER TABLE main.{old} RENAME TO {new}")
    elif new == "mrt_atom_references":
        connection.execute(f"ALTER VIEW main.{old} RENAME TO {new}")
    elif old in PUBLIC_NAMES or old in DOMAIN_COMPATIBILITY:
        connection.execute(f"DROP VIEW main.{old}")


def _migrate_graph_tables(connection):
    rows = connection.execute(
        "SELECT table_schema, table_name FROM information_schema.tables "
        "WHERE table_catalog = current_database() AND table_type = 'BASE TABLE' "
        "AND table_schema IN ('native_graph', 'realization_internal')"
    ).fetchall()
    for schema, name in rows:
        if schema == "native_graph":
            if name not in ("labels", "reference") and not re.fullmatch(r"relation_[0-9]+", name):
                continue
        elif name not in _REALIZATION_WORK:
            continue
        connection.execute(f"ALTER TABLE {schema}.{name} RENAME TO int_{name}")
