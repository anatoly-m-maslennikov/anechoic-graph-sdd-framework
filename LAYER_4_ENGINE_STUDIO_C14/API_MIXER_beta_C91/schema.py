"""Validate the Kernel's public SQL schema."""

import httpx2
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .admission import failure, peer


TABLES = (
    "atoms",
    "native_references",
    "relations",
    "import_nodes",
    "module_imports",
    "import_edges",
    "package_imports",
    "test_edges",
    "tested_by_edges",
    "import_read_issues",
    "package_external_imports",
    "state_effect_findings",
    "code_access_findings",
    "code_units",
    "code_unit_calls",
    "import_cycles",
    "package_coupling",
    "antipattern_findings",
    "architecture_code_metrics",
    "architecture_spec_metrics",
    "architecture_ratios",
    "package_review_profiles",
    "package_largest_files",
    "architecture_package_bindings",
)
FLOWS = (
    "component_flows",
    "flow_events",
    "flow_overlap_candidates",
    "flow_similar_actions",
)
BIZ = (
    "package_coupling",
    "architecture_code_metrics",
    "architecture_spec_metrics",
    "architecture_ratios",
    "package_review_profiles",
    "package_largest_files",
)
ALIASES = {
    f"{'biz' if name in BIZ else 'mrt'}_{name}": name for name in TABLES
}
ALIASES.update(
    {
        f"{'src' if name == 'flow_events' else 'mrt'}_{name}": name
        for name in FLOWS
    }
)
ALIASES.update(
    {
        f"mrt_{name}": name
        for name in (
            "project_structure",
            "model_entities",
            "model_properties",
            "model_tree",
            "model_primary_entities",
            "diag_model_manifests",
        )
    }
)
ALIASES.update({f"ops_{name}": name for name in ("work_journal", "query_log")})
ALIASES.update(
    {
        f"mrt_real_graph_{name}": name
        for name in (
            "import_edges",
            "package_imports",
            "package_external_imports",
            "code_units",
            "code_unit_calls",
            "test_edges",
            "tested_by_edges",
        )
    }
)
ALIASES.update(
    {
        "mrt_atom_graph_relations": "relations",
        "mrt_atom_references": "native_references",
        "mrt_flow_actions": "component_flows",
        "mrt_real_graph_import_nodes": "import_nodes",
        "mrt_real_graph_import_occurrences": "module_imports",
        ("mrt_real_graph_package_spec_bindings"): (
            "architecture_package_bindings"
        ),
        "mrt_diag_import_read_issues": "import_read_issues",
        "mrt_diag_import_cycles": "import_cycles",
        "mrt_diag_antipatterns": "antipattern_findings",
        "mrt_diag_code_access": "code_access_findings",
        "mrt_diag_state_effects": "state_effect_findings",
        **{
            f"mrt_{family}_atoms": "atoms"
            for family in ("spec", "ticket", "project_config")
        },
    }
)


class SchemaColumn(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    values: list[str] | None = None


class Schema(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    tables: dict[str, list[SchemaColumn]]

    @model_validator(mode="after")
    def valid_tables(self):
        allowed = {
            *TABLES,
            *FLOWS,
            "work_journal",
            "query_log",
            "ops_ingestion_issues",
            *ALIASES,
            *ALIASES.values(),
        }
        for table, columns in self.tables.items():
            if table not in allowed or len(
                {column.name for column in columns}
            ) != len(columns):
                raise ValueError("Invalid Kernel schema")
            for column in columns:
                if "values" in column.model_fields_set:
                    values = column.values
                    if (
                        ALIASES.get(table, table) != "atoms"
                        or column.name != "header.state.status"
                        or values is None
                        or not 1 <= len(values) <= 256
                        or len(set(values)) != len(values)
                        or any(len(v.encode("utf-8")) > 1024 for v in values)
                    ):
                        raise ValueError("Invalid Kernel schema")
        return self


async def read_schema(database, instance, arguments):
    if arguments:
        return failure(
            "tool_input_invalid", "The schema request has no arguments"
        )
    try:
        value = (
            await peer(
                database, "GET", "/schema", params={"instance_id": instance}
            )
        )["result"]
        Schema.model_validate(value)
        return {"result": {"value": value, "text": None}}
    except httpx2.HTTPError, ValueError, TypeError, KeyError, UnicodeError:
        return failure("workbench_unavailable", "Kernel schema unavailable")
