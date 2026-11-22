
"""Generate the deterministic Workbench schema asset from one Project capture."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__:
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import _source, content_schema_from_statements, declaration_statements
    from .declared_classifications import compile_status_groups
    from KERNEL_MIXER_C59.declared_header_rules import header_rules_from_statements
    from KERNEL_MIXER_C59.header_columns import declared_header_schema
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import formal_claim_fences, source_markdown
    from .source_reader import SourceReader
    from KERNEL_MIXER_C59.source_selection import first_reference_rows
    from .workbench_schema_asset import compile_schema, schema_asset
else:  # pragma: no cover - direct image-build invocation
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import _source, content_schema_from_statements, declaration_statements
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.declared_classifications import compile_status_groups
    from KERNEL_MIXER_C59.declared_header_rules import header_rules_from_statements
    from KERNEL_MIXER_C59.header_columns import declared_header_schema
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import formal_claim_fences, source_markdown
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_reader import SourceReader
    from KERNEL_MIXER_C59.source_selection import first_reference_rows
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workbench_schema_asset import compile_schema, schema_asset

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import is_current_requirement_declaration
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import compile_role_folders


def compile_project_schema(project_root: Path, *, model_class_bindings=None) -> bytes:
    """Capture one Project and compile both admitted Workbench schema modes."""
    reader = SourceReader(Path(project_root), include_archived=False, include_installed_framework=True)
    atoms, _scopes = reader.capture()
    selected = list(first_reference_rows(reader.model_rows(atoms, is_current_requirement_declaration)))
    if model_class_bindings is None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_catalog__pub import bindings_from_workbench_rows
        model_class_bindings = bindings_from_workbench_rows(selected)
    pins = {}
    statements = []
    for row in selected:
        row = {**row, "_model_class_bindings": model_class_bindings}
        claim = declaration_statements(row)
        if claim:
            statements.extend(claim)
            pins[row["source_path"]] = row
    content = content_schema_from_statements(statements)
    header = declared_header_schema(header_rules_from_statements(statements))
    folders = compile_role_folders(statements)
    role_folders = tuple(sorted((role, folder) for role, (folder, _source) in folders.items())) if folders else None
    status_groups = compile_status_groups(_python_declarations(selected))
    return schema_asset(list(pins.values()), compile_schema(atoms, content, header, status_groups, role_folders))


def _python_declarations(rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.python_claim__pub import parse_structured_python_model_claim

    for row in rows:
        if not is_current_requirement_declaration(row):
            continue
        body = source_markdown(row)
        if body is None:
            continue
        source = _source(row)
        for language, claim in formal_claim_fences(body):
            if language != "python":
                continue
            native = parse_native_model_claim(claim)
            if native is not None:
                yield native, source
            else:
                for declaration in parse_structured_python_model_claim(claim):
                    yield declaration, source


def write_schema(output: Path, data: bytes) -> None:
    """Write the caller-selected generated-asset target."""
    Path(output).write_bytes(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    write_schema(args.output, compile_project_schema(args.project_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
