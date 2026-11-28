"""Select staged native Model Claims in the previous runtime image."""

from contextlib import redirect_stdout
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path("/workspace")
ENGINE_ROOT = ROOT / "LAYER_4_ENGINE_STUDIO_C14"
if not ENGINE_ROOT.is_dir():
    ENGINE_ROOT = ROOT / "LAYER_3_ENGINE_STUDIO_C14"
PROGRAMMATIC = ENGINE_ROOT / "FEATURE_PROGRAMMATIC"
sys.path[:0] = list(
    map(
        str,
        (
            ENGINE_ROOT,
            ROOT,
            PROGRAMMATIC,
            PROGRAMMATIC / "FEATURE_TOOLS",
            ENGINE_ROOT / "IWE_CONSOLE_C43",
            ENGINE_ROOT / "MCP_PATCHBAY_C21/FEATURE_MCP",
        ),
    )
)


def _workbench_types():
    if (
        ENGINE_ROOT.name == "LAYER_4_ENGINE_STUDIO_C14"
        or (ENGINE_ROOT / "pyproject.toml").is_file()
    ):
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
            compile_content_schema,
        )
        from KERNEL_MIXER_C59.header_columns import HeaderColumn, HeaderSchema
        from KERNEL_MIXER_C59.query_store import QueryStore
    elif (ENGINE_ROOT / "KERNEL_MIXER_C59/query_store.py").is_file():
        # import-graph: previous-image
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.content_schema import (
            compile_content_schema,
        )

        # import-graph: previous-image
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.header_columns import (
            HeaderColumn,
            HeaderSchema,
        )

        # import-graph: previous-image
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.query_store import (
            QueryStore,
        )
    else:
        # import-graph: previous-image
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.content_schema import (
            compile_content_schema,
        )

        # import-graph: previous-image
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.header_columns import (
            HeaderColumn,
            HeaderSchema,
        )

        # import-graph: previous-image
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import (
            QueryStore,
        )
    return compile_content_schema, HeaderColumn, HeaderSchema, QueryStore


def _claim_subject(header, body):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.content.markdown_content__pub import (parse_content)  # fmt: skip

    context = header.get("context", {})
    lens, template = context.get("lens"), context.get("template")
    scopes = [
        section["direct_markdown"]
        for section in parse_content(body, tolerate_duplicate_siblings=True)
        if section["property_path"] == ["claim_scope"]
    ]
    subject = next(
        (
            scope
            for scope in scopes
            if isinstance(scope, str) and "MODEL//ANECHOIC" in scope
        ),
        None,
    )
    if lens == "DOM/CONT" and template in {
        "manifest_node",
        "manifest_property",
        "manifest_relation",
    }:
        concern = header.get("concern")
        if (
            isinstance(concern, dict)
            and set(concern) == {"subject", "path", "relation"}
            and all(
                isinstance(value, str) and value.strip()
                for value in concern.values()
            )
        ):
            return "Continuant Concern"
        return None
    if template == "manifest_property" and lens in {"SPEC", "DES"}:
        return subject or "typed Property"
    return subject if lens == "SPEC" else None


def _collect_rows(component: Path):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.content.carrier_read__pub import (parse_carrier)  # fmt: skip
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        carriers.header.native_carrier_header__pub import (native_header_view)  # fmt: skip
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        sources.inventory.source_row__pub import (atom)  # fmt: skip

    rows, hashes = [], {}
    paths = (
        list(component.glob("*.md"))
        + list((component / "_DES").glob("*.md"))
        + list((component / "_DOM" / "CONT").glob("*.md"))
    )
    for path in sorted(paths):
        raw = path.read_bytes()
        carrier = parse_carrier(raw, path)
        metadata = dict(carrier.metadata)
        if "container" in metadata and "structure" not in metadata:
            metadata["structure"] = {
                name: metadata.pop(name)
                for name in ("container", "tier", "priority")
                if name in metadata
            }
        header = native_header_view(metadata)
        context, state = header.get("context", {}), header.get("state", {})
        if context.get("container") != {"component": "C9"}:
            continue
        metadata = {
            "lens": context.get("lens"),
            "status": state.get("status"),
            "subject": _claim_subject(header, carrier.body),
        }
        row = atom(
            path,
            component,
            metadata,
            {"atom_id": path.name, "version": 1},
            b"",
            "Current",
        )
        rows.append(row)
        hashes[path.name] = sha256(raw).hexdigest()

    return rows, hashes


def select_claims(component: Path) -> list[list[str]]:
    rows, hashes = _collect_rows(component)

    if (
        not (ENGINE_ROOT / "KERNEL_MIXER_C59").is_dir()
        and (ENGINE_ROOT / "KERNEL_MIXER_beta_C67").is_dir()
    ):
        return _beta_selected(rows, hashes)
    compile_content_schema, HeaderColumn, HeaderSchema, QueryStore = (
        _workbench_types()
    )
    schema = HeaderSchema(
        tuple(
            HeaderColumn((key,), "header." + key, "VARCHAR", True)
            for key in ("lens", "status", "subject")
        )
    )
    store = QueryStore()
    try:
        store.replace(
            rows,
            [],
            relation_types=set(),
            header_schema=schema,
            content_schema=compile_content_schema([]),
        )
        result = store.run(
            "SELECT filename FROM atoms WHERE \"header.status\" = 'active' "
            'AND "header.subject" IS NOT NULL ORDER BY filename',
            page_size=1000,
        )
        return _selected_pages(store, result, hashes)
    finally:
        store.close()


def _beta_selected(rows, hashes):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.query_engine import (
        connect,
    )

    connection = connect(":memory:")
    try:
        connection.execute(
            (
                "CREATE TABLE model_sources (filename VARCHAR, status "
                "VARCHAR, subject VARCHAR)"
            )
        )
        values = [
            (
                Path(row["source_path"]).name,
                row["header_json"]["status"],
                row["header_json"]["subject"],
            )
            for row in rows
        ]
        if values:
            connection.executemany(
                "INSERT INTO model_sources VALUES (?, ?, ?)", values
            )
        selected = connection.execute(
            (
                "SELECT filename FROM model_sources WHERE status = 'active' "
                "AND subject IS NOT NULL ORDER BY filename"
            )
        ).fetchall()
        return [[name, hashes[name]] for (name,) in selected]
    finally:
        connection.close()


def _selected_pages(store, result, hashes):
    selected = []
    while True:
        selected.extend([name, hashes[name]] for (name,) in result["rows"])
        if not result["has_more"]:
            return selected
        result = store.page(result["query_id"], len(selected), page_size=1000)


if __name__ == "__main__":
    with redirect_stdout(sys.stderr):
        selected = select_claims(Path(sys.argv[1]))
    print(json.dumps(selected))
