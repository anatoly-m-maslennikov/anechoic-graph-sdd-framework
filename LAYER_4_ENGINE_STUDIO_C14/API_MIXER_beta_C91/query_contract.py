"""Generate the query_run wire contract from its owning Pydantic model."""

from argparse import ArgumentParser
import json
from pathlib import Path

from .models import Query

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


def typescript_text():
    schema = query_schema()
    types = {"string": "string", "integer": "number", "boolean": "boolean"}
    lines = ["export type QueryRun = {"]
    for name, field in schema["properties"].items():
        if "enum" in field:
            value = " | ".join(json.dumps(item) for item in field["enum"])
        else:
            value = types[field["type"]]
        optional = "" if name in schema["required"] else "?"
        lines.append(f"  {name}{optional}: {value};")
    return "\n".join([*lines, "};", ""])


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
