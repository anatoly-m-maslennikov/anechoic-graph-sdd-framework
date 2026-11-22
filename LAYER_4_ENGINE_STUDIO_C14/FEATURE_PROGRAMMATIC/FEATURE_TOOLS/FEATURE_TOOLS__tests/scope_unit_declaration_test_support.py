"""Shared temporary Scope Unit declaration trees for reader tests."""
from pathlib import Path
import tempfile

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import PROJECT, render_scope_declaration


class ScopeUnitFixture:
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.control = self.root / ".anechoic_demo"
        self.control.mkdir()
        (self.control / "anechoic_project_settings.toml").write_text(
            '[project]\nname = "demo"\n[paths]\ncontrol_root = ".anechoic_demo"\n[artifacts.identity]\nproject_prefix = "ca"\n', encoding="utf-8",
        )

    def declaration(
        self, name: str, atom_id: str, *, source: Path | None = None, scope_id: str | None = None,
        label: str | None = None, ordered: bool = False, order_number: int | None = None,
        parent: str | None = None, project: bool = False, project_name: str = "demo",
    ) -> Path:
        source = source or self.control / "04_requirement" / f"{atom_id}-{name}.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(render_scope_declaration(
            name=name, project_name=project_name, atom_id=atom_id, updated_at="2026-11-02 00:00:00 +0000",
            scope_id=scope_id, label=label, ordered=ordered, order_number=order_number,
            parent=parent, project=project,
        ), encoding="utf-8")
        return source

    def complete_tree(self) -> tuple[Path, Path, Path]:
        root = self.declaration("demo", "CA-R-1", source=self.control / "CA-R-1-demo.md", project=True)
        parent = self.declaration(
            "PARENT", "CA-R-2", scope_id="CA-SU-1", label="LAYER", ordered=True,
            order_number=1, parent=PROJECT,
        )
        child = self.declaration(
            "CHILD", "CA-R-3", source=self.control / "CA-SU-1_LAYER_1_PARENT" / "04_requirement" / "child.md",
            scope_id="CA-SU-2", label="FEATURE", parent="PARENT",
        )
        return root, parent, child
