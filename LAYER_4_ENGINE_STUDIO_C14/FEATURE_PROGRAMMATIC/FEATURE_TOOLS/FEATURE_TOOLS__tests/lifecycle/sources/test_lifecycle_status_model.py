import json
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

TOOLS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (  # noqa: E402
    StatusModelError,
    canonical_status,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (  # noqa: E402
    StatusModel,
    compile_status_model,
    load_status_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_compat__pub import (  # noqa: E402
    carrier_read_view,
)

CORE = (
    Path(__file__).resolve().parents[2]
    / "assets/lifecycle_schema_declarations/04_requirement"
)


class StatusModelTests(unittest.TestCase):
    def test_carrier_values_and_collision(self):
        model = StatusModel(((None, None, "In Progress"),))
        self.assertEqual(
            canonical_status(model, "Plan", "Task", "in_progress"),
            "In Progress",
        )
        self.assertEqual(
            canonical_status(model, "Plan", "Task", "In Progress"),
            "In Progress",
        )
        with self.assertRaises(StatusModelError):
            canonical_status(model, "Plan", "Task", "IN_PROGRESS")
        collision = StatusModel(
            ((None, None, "In Progress"), (None, None, "In_Progress"))
        )
        with self.assertRaises(StatusModelError):
            canonical_status(collision, "Plan", "Task", "In Progress")

    def sources(self):
        return [
            next(CORE.rglob(f"CA-R-{number}-*.md"))
            for number in (2696, 1539, 1608, 1875)
        ]

    def test_sealed_sources_inheritance_and_union(self):
        sources = self.sources()
        payload = compile_status_model(sources)
        asset = json.loads(payload)
        headers = [
            carrier_read_view(
                yaml.safe_load(path.read_text().split("---", 2)[1])
            )
            for path in sources
        ]
        self.assertEqual(10, len(asset["declarations"]))
        self.assertEqual(
            {header["atom_id"]: header["version"] for header in headers},
            {
                source["atom_id"]: source["version"]
                for source in asset["sources"]
            },
        )
        self.assertEqual(payload, compile_status_model(reversed(sources)))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            path.write_bytes(payload)
            model = load_status_model(path)
            base = {"Draft", "Active", "Archived"}
            self.assertEqual(base, model.allowed("Requirement", "Declaration"))
            self.assertEqual(
                base | {"Backlog", "Done", "Canceled"},
                model.allowed("Plan", "Plan"),
            )
            self.assertEqual(
                base | {"Resolved", "Canceled"},
                model.allowed("Concern", "Issue"),
            )
            self.assertEqual(
                base | {"Done"},
                model.allowed("Analysis and Advisory", "Rationale"),
            )
            self.assertEqual(
                base, model.allowed("Analysis and Advisory", "Other")
            )
            self.assertEqual(
                base, model.allowed("Analysis and Advisory", "Code Synopsis")
            )
            self.assertEqual(base, model.allowed("Other", "Code Synopsis"))

    def test_role_and_form_domains_are_unioned(self):
        source = (
            self.sources()[3]
            .read_text()
            .replace('"Analysis and Advisory"', '"Plan"')
            .replace('("Analysis Report", "Rationale")', '("Report",)')
            .replace('("Done",)', '("Reviewed",)')
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.md"
            path.write_text(source)
            payload = compile_status_model(
                [self.sources()[0], self.sources()[1], path]
            )
            path.write_bytes(payload)
            self.assertEqual(
                {
                    "Draft",
                    "Active",
                    "Archived",
                    "Backlog",
                    "Done",
                    "Canceled",
                    "Reviewed",
                },
                load_status_model(path).allowed("Plan", "Report"),
            )

    def test_backlog_group_is_not_a_status_membership_and_malformed_refuses(
        self,
    ):
        sources = self.sources()
        current = sources[1].read_text()
        group = 'status_groups={"Backlog": "Backlog"},'
        self.assertIn(group, current)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            path.write_text(current.replace(group, ""))
            self.assertEqual(
                json.loads(compile_status_model(sources))["declarations"],
                json.loads(
                    compile_status_model([sources[0], path, *sources[2:]])
                )["declarations"],
            )
            for malformed, diagnostic in (
                (
                    "status_groups=None,",
                    "Status Groups require allowed values and one Role",
                ),
                (
                    'status_groups={"Unlisted": "Backlog"},',
                    "Status Groups require allowed values and one Role",
                ),
                (
                    'status_group={"Backlog": "Backlog"},',
                    "unsupported declare_entity arguments: status_group",
                ),
            ):
                with self.subTest(malformed=malformed):
                    path.write_text(current.replace(group, malformed))
                    with self.assertRaisesRegex(ValueError, diagnostic):
                        compile_status_model([sources[0], path])

    def test_plan_constraints_do_not_add_status_memberships(self):
        sources = self.sources()
        plan = next(CORE.rglob("CA-R-2511-*.md"))
        base = json.loads(compile_status_model(sources))
        compiled = json.loads(compile_status_model([*sources, plan]))
        self.assertEqual(base["declarations"], compiled["declarations"])

    def test_cli_reads_only_current_staged_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "sources"
            sources.mkdir()
            for path in self.sources():
                (sources / path.name).write_bytes(path.read_bytes())
            archived = sources / "archive"
            archived.mkdir()
            (archived / self.sources()[0].name).write_text("invalid")
            _, header, body = self.sources()[1].read_text().split("---", 2)
            metadata = yaml.safe_load(header)
            metadata.get("state", metadata)["status"] = "draft"
            (sources / "CA-R-9999-draft.md").write_text(
                "---\n" + yaml.safe_dump(metadata) + "---" + body
            )
            output = root / "asset.json"
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOLS / "ATOM_LIFECYCLE/status_model.py"),
                    "--model-root",
                    str(sources),
                    "--output",
                    str(output),
                ],
                check=True,
            )
            self.assertEqual(
                compile_status_model(self.sources()), output.read_bytes()
            )

    def test_grouped_headers_and_native_status_values(self):
        original = self.sources()[0].read_text()
        _, header, body = original.split("---", 2)
        metadata = yaml.safe_load(header)
        for group, names in {
            "identity": ("atom_id", "ref_id"),
            "context": ("container", "role", "form", "topics", "tier"),
            "state": ("status", "version", "updated_at"),
        }.items():
            metadata[group] = {
                name: metadata.pop(name) for name in names if name in metadata
            }
        body = body.replace('"Active"', '"Live #1"')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "sources"
            sources.mkdir()
            source = sources / self.sources()[0].name
            source.write_text(
                "---\n"
                + yaml.safe_dump(metadata, sort_keys=False)
                + "---"
                + body
            )
            output = root / "asset.json"
            subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(TOOLS / "ATOM_LIFECYCLE/status_model.py"),
                    "--model-root",
                    str(sources),
                    "--output",
                    str(output),
                ],
                check=True,
            )
            self.assertEqual(
                {"Draft", "Live #1", "Archived"},
                load_status_model(output).allowed("Plan", "Plan"),
            )

    def test_asset_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            for data in (
                "{}",
                '{"schema":1,"schema":1}',
                '{"schema":1,"sources":[],"declarations":[]}',
            ):
                path.write_text(data)
                with self.assertRaises(StatusModelError):
                    load_status_model(path)


if __name__ == "__main__":
    unittest.main()
