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
sys.path[:0] = list(map(str, (
    ENGINE_ROOT, ROOT, PROGRAMMATIC, PROGRAMMATIC / "FEATURE_TOOLS", ENGINE_ROOT / "IWE_CONSOLE_C43",
    ENGINE_ROOT / "MCP_PATCHBAY_C21/FEATURE_MCP",
)))


def _workbench_types():
    if ENGINE_ROOT.name == "LAYER_4_ENGINE_STUDIO_C14" or (ENGINE_ROOT / "pyproject.toml").is_file():
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_content_schema
        # Previous images can predate the shared exports for these types.
        from KERNEL_MIXER_C59.header_columns import HeaderColumn, HeaderSchema
        from KERNEL_MIXER_C59.query_store import QueryStore
    elif (ENGINE_ROOT / "KERNEL_MIXER_C59/query_store.py").is_file():
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.content_schema import compile_content_schema
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.header_columns import HeaderColumn, HeaderSchema
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.query_store import QueryStore
    else:
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.content_schema import compile_content_schema
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.header_columns import HeaderColumn, HeaderSchema
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
    return compile_content_schema, HeaderColumn, HeaderSchema, QueryStore


def select_claims(component: Path) -> list[list[str]]:
    # The staging command mounts these codec modules in the previous image.
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import parse_content
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_row__pub import atom
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import native_header_view
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier

    compile_content_schema, HeaderColumn, HeaderSchema, QueryStore = _workbench_types()
    rows, hashes = [], {}
    for path in sorted(component.glob("*.md")):
        raw = path.read_bytes()
        carrier = parse_carrier(raw, path)
        metadata = dict(carrier.metadata)
        if "container" in metadata and "structure" not in metadata:
            metadata["structure"] = {name: metadata.pop(name) for name in ("container", "tier", "priority")
                                     if name in metadata}
        header = native_header_view(metadata)
        context, state = header.get("context", {}), header.get("state", {})
        if context.get("container") != {"component": "C9"}:
            continue
        scopes = [section["direct_markdown"] for section in
                  parse_content(carrier.body, tolerate_duplicate_siblings=True)
                  if section["property_path"] == ["claim_scope"]]
        subject = next((scope for scope in scopes if isinstance(scope, str)
                        and "MODEL//ANECHOIC" in scope), None)
        metadata = {"lens": context.get("lens"), "status": state.get("status"), "subject": subject}
        row = atom(path, component, metadata, {"atom_id": path.name, "version": 1}, b"", "Current")
        rows.append(row)
        hashes[path.name] = sha256(raw).hexdigest()

    schema = HeaderSchema(tuple(HeaderColumn((key,), "header." + key, "VARCHAR", True)
                                for key in ("lens", "status", "subject")))
    store = QueryStore()
    try:
        store.replace(rows, [], relation_types=set(), header_schema=schema,
                      content_schema=compile_content_schema([]))
        result = store.run(
            'SELECT filename FROM atoms WHERE "header.lens" = \'SPEC\' '
            'AND "header.status" = \'active\' AND "header.subject" IS NOT NULL ORDER BY filename',
            page_size=1000,
        )
        return _selected_pages(store, result, hashes)
    finally:
        store.close()


def _selected_pages(store, result, hashes):
    selected = []
    while True:
        selected.extend([name, hashes[name]] for name, in result["rows"])
        if not result["has_more"]:
            return selected
        result = store.page(result["query_id"], len(selected), page_size=1000)


if __name__ == "__main__":
    with redirect_stdout(sys.stderr):
        selected = select_claims(Path(sys.argv[1]))
    print(json.dumps(selected))
