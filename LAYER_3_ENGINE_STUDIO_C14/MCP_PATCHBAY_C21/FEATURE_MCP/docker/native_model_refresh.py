"""Select staged native Model Claims with Workbench and compile them for image admission."""

from contextlib import redirect_stdout
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory


ENGINE = "LAYER_3_ENGINE_STUDIO_C14"
ONTOLOGY = "LAYER_1_META_ONTOLOGY_C9"
ROOT = Path("/workspace") if Path(__file__) == Path("/selector.py") else Path(__file__).resolve().parents[4]
ENGINE_ROOT = ROOT / ENGINE
PROGRAMMATIC = ENGINE_ROOT / "FEATURE_PROGRAMMATIC"
sys.path[:0] = list(map(str, (
    ROOT, PROGRAMMATIC, PROGRAMMATIC / "FEATURE_TOOLS", ENGINE_ROOT / "IWE_CONSOLE_C43",
    ENGINE_ROOT / "MCP_PATCHBAY_C21/FEATURE_MCP",
)))


def select_claims(component: Path) -> list[list[str]]:
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.content_schema import compile_content_schema
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.header_columns import HeaderColumn, HeaderSchema
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.markdown_content import parse_content
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
    from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import atom
    from native_carrier_header import native_header_view
    from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier

    rows, hashes = [], {}
    for path in sorted(component.glob("*.md")):
        raw = path.read_bytes()
        carrier = parse_carrier(raw, path)
        header = native_header_view(carrier.metadata)
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
        selected = []
        while True:
            selected.extend([name, hashes[name]] for name, in result["rows"])
            if not result["has_more"]:
                return selected
            result = store.page(result["query_id"], len(selected), page_size=1000)
    finally:
        store.close()


def previous_claims(component: Path, image: str, *, timeout: float) -> list[list[str]]:
    from image_docker_client import bounded_run
    from image_reference import IMMUTABLE_IMAGE

    if IMMUTABLE_IMAGE.fullmatch(image) is None:
        raise ValueError("Previous image must be an immutable image ID")
    result = bounded_run(["docker", "image", "inspect", image], cwd=ROOT, timeout=timeout)
    if result.returncode:
        raise ValueError("Previous ready image is unavailable")
    [details] = json.loads(result.stdout)
    if (details.get("Id") != image or details.get("Os") != "linux"
            or (details["Config"]["Labels"] or {}).get("org.anechoic.runtime.schema") != "1"):
        raise ValueError("Previous ready image is not an admitted runtime image")

    selector = component.parent / "selector.py"
    shutil.copyfile(__file__, selector)
    if any(set(str(path)) & {",", "\n", "\r"} for path in (component, selector)):
        raise ValueError("Native selector mount path is invalid")
    result = bounded_run([
        "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only",
        "--mount", f"type=bind,src={component},dst=/model,readonly",
        "--mount", f"type=bind,src={selector},dst=/selector.py,readonly",
        "--entrypoint", "/opt/venv/bin/python", image, "/selector.py", "/model",
    ], cwd=ROOT, timeout=timeout, report_stderr=True)
    if result.returncode:
        raise ValueError("Previous ready image could not select native Model Claims")
    return json.loads(result.stdout)


def verify_project_model(project: Path, timeout: float, previous: str | None) -> str:
    from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.compiler import write_model
    from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_pkg2.host import verify_model
    from native_startup import select_runtime_project
    from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
    from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS

    control = select_runtime_project(project).control_root
    source = control / ONTOLOGY
    if not source.exists() and not source.is_symlink():
        from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import reviewed_model_records

        return reviewed_model_records()[2]
    reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))
    temporary = project / ".anechoic_tmp"
    if temporary.is_symlink() or not temporary.is_dir():
        raise ValueError("Native Model staging root is unavailable")
    with TemporaryDirectory(prefix="anechoic-image-model-", dir=temporary) as stage:
        staged = Path(stage) / ONTOLOGY
        staged.mkdir()
        hashes = {}
        for path in reader.inventory_shallow(source):
            raw = reader.read(path)
            (staged / path.name).write_bytes(raw)
            hashes[path.name] = sha256(raw).hexdigest()
        selected = previous_claims(staged, previous, timeout=timeout) if previous else None
        fingerprint = write_model(staged.parent, staged.parent)
        verify_model(staged.parent, fingerprint)
        if previous:
            records = json.loads((staged.parent / "model.json").read_text())["declarations"]
            names = [Path(location.rsplit("@", 1)[0]).name for location, _, _ in records]
            if selected != [[name, hashes[name]] for name in sorted(names)]:
                raise ValueError("Previous image selection does not match the current native Model sources")
        if reader.currentness()["state"] != "unchanged":
            raise ValueError("Native Model sources changed during refresh")
        return fingerprint


if __name__ == "__main__":
    if Path(__file__) == Path("/selector.py"):
        with redirect_stdout(sys.stderr):
            selected = select_claims(Path(sys.argv[1]))
        print(json.dumps(selected))
    else:
        print(verify_project_model(Path(sys.argv[1]), float(sys.argv[2]),
                                   sys.argv[3] if len(sys.argv) == 4 else None))
