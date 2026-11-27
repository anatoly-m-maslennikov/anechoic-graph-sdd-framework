from __future__ import annotations

from contextlib import contextmanager, redirect_stderr
from io import StringIO
from pathlib import Path
import tempfile
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import SourceReader  # noqa: E402




class SourceReaderFixture:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.control = self.root / ".anechoic_anechoic"
        self.control.mkdir()
        (self.control / "anechoic_project_settings.toml").write_text(
            '[project]\nname = "fixture"\n[artifacts.identity]\nproject_prefix = "CA"\n'
            '[paths]\ncontrol_root = ".anechoic_anechoic"\n',
            encoding="utf-8",
        )
        self.declarations = write_scope_unit_declarations(
            self.root,
            (
                {
                    "scope_unit_name": "MAIN",
                    "scope_unit_type": "Ordered",
                    "scope_unit_label": "LAYER",
                    "local_order": 1,
                },
                {"scope_unit_name": "CHILD", "parent": "MAIN", "scope_unit_label": "FEATURE"},
            ),
            control_root=self.control,
        )
        self.reader = SourceReader(self.root)


    def _path(self, scope: str, role: str, filename: str, *parts: str) -> Path:
        if not filename.startswith(("CA-", "ANECHOIC-")) and filename not in {"README.md", "REPORT.md"}:
            filename = "CA-R-" + filename
        path = Path(self.declarations[scope]["authority_path"]) / role
        if parts:
            path = path.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path / filename


    def _write_atom(
        self,
        scope: str,
        role: str,
        filename: str,
        *,
        atom_id: str,
        status: str = "Active",
        version: int = 1,
        form: str = "Definition",
        body: str = "# Summary\n\nFixture source.\n",
        parts: tuple[str, ...] = (),
    ) -> Path:
        path = self._path(scope, role, filename, *parts)
        path.write_text(
            "---\n"
            f'atom_id: "{atom_id}"\n'
            'role: "Requirement"\n'
            f'form: "{form}"\n'
            f'status: "{status}"\n'
            f"version: {version}\n"
            'updated_at: "2026-11-04 00:00:00 +0000"\n'
            "subjects: {}\n"
            "relations: {}\n"
            "---\n"
            + body,
            encoding="utf-8",
        )
        return path


    def _capture(self) -> tuple[list[dict], list[dict], str]:
        stderr = StringIO()
        with redirect_stderr(stderr):
            atoms, scopes = self.reader.capture()
        return atoms, scopes, stderr.getvalue()


    @contextmanager
    def source_reads(self):
        paths = []
        original_read = ReadContext.read

        def record(context, path, **kwargs):
            paths.append(Path(path).resolve())
            return original_read(context, path, **kwargs)

        with patch.object(ReadContext, "read", new=record):
            yield paths


    def declaration_paths(self) -> set[Path]:
        return {Path(row["declaration_path"]).resolve() for row in self.declarations.values()}


    def _snapshot_files(self) -> dict[Path, bytes]:
        return {
            path: path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }


