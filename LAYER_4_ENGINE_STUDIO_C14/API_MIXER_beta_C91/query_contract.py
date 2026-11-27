"""Generate query wire types from the owning Pydantic models."""

from argparse import ArgumentParser
import json
from pathlib import Path

from .models import Page, Query
from ._shared_runtime_support import TOOL_REST_PATH

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = Path(__file__).with_name("query_run.schema.json")
TYPE_PATH = ROOT / (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE"
    "_CONSOLE_FRONTEND/src/lib/query_run.generated.ts"
)


def query_schema():
    """Describe the wire fields, which reject explicit nulls."""
    schema = Query.model_json_schema()
    schema.pop("title")
    for name, field in schema["properties"].items():
        field.pop("title", None)
        if "anyOf" in field:
            variants = field.pop("anyOf")
            non_null = [item for item in variants if item != {"type": "null"}]
            if len(variants) != 2 or len(non_null) != 1:
                raise ValueError(f"Unsupported nullable schema for {name}")
            field.update(non_null[0])
        if name != "save":
            field.pop("default", None)
    return schema


def schema_text():
    return json.dumps(query_schema(), indent=2, sort_keys=True) + "\n"


def _typescript_type(field):
    if "enum" in field:
        return " | ".join(json.dumps(item) for item in field["enum"])
    if field.get("$ref") == "#/$defs/Column":
        return "QueryColumn"
    if field["type"] == "array":
        return f"Array<{_typescript_type(field['items'])}>"
    return {"string": "string", "integer": "number", "boolean": "boolean"}[
        field["type"]
    ]


def _typescript_declaration(name, schema, fields=None):
    properties = schema["properties"]
    required = schema.get("required", ())
    if fields is None:
        fields = properties
    lines = [f"export type {name} = {{"]
    for field in fields:
        optional = "" if field in required else "?"
        value = _typescript_type(properties[field])
        lines.append(f"  {field}{optional}: {value};")
    return "\n".join([*lines, "};", ""])


def typescript_text():
    page = Page.model_json_schema()
    return "\n".join(
        (
            f"export const TOOL_REST_PATH = {json.dumps(TOOL_REST_PATH)};\n",
            _typescript_declaration("QueryRun", query_schema()),
            _typescript_declaration("QueryColumn", page["$defs"]["Column"]),
            _typescript_declaration("QueryPageCore", page, page["required"]),
        )
    )


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, generated in (
        (SCHEMA_PATH, schema_text()),
        (TYPE_PATH, typescript_text()),
    ):
        if args.check:
            if path.read_text(encoding="utf-8") != generated:
                parser.error(f"Generated query contract is stale: {path}")
        else:
            path.write_text(generated, encoding="utf-8")


if __name__ == "__main__":
    main()
