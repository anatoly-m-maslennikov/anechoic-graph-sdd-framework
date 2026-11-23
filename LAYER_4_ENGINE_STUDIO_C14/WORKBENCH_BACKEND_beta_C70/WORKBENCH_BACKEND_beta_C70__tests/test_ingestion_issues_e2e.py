"""Exercise ingestion diagnostics through the real shared Beta Gateway."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .test_shared_beta import _backend, _invoke, _project, _settings


class IngestionIssuesEndToEndTests(unittest.IsolatedAsyncioTestCase):
    async def test_first_failed_capture_exposes_diagnostics_in_status(self):
        with TemporaryDirectory(prefix="ane-beta-ingestion-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            project, manifest = _project(projects, "broken")
            ticket = manifest.parent / "__TKT" / "AN-T-1--task.md"
            ticket.parent.mkdir()
            ticket.write_text("---\nidentity: [invalid\n")
            async with _backend(root, _settings(root, projects)) as (http, _):
                refused = await _invoke(http, project)
                self.assertIn("error", refused, refused)
                status = await _invoke(http, project, "workbench_status", {})
                issues = status["result"]["value"]["ingestion_issues"]
                self.assertTrue(any(
                    issue["source"] == "atom" and issue["code"] == "parse_error"
                    and issue["relative_path"] == ticket.relative_to(project).as_posix()
                    for issue in issues
                ), issues)

    async def test_failed_rebuild_preserves_atoms_and_reports_issue_until_repaired(self):
        with TemporaryDirectory(prefix="ane-beta-ingestion-", dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            projects = root / "projects"
            projects.mkdir()
            project, manifest = _project(projects, "accepted")
            ticket = manifest.parent / "__TKT" / "AN-T-1--task.md"
            ticket.parent.mkdir()
            settings = _settings(root, projects)

            async with _backend(root, settings) as (http, _):
                async def rows(sql):
                    response = await _invoke(http, project, arguments={
                        "sql": sql, "result_delivery": "inline",
                        "cursor_position": 0, "page_size": 100,
                    })
                    self.assertIn("result", response, response)
                    return response["result"]["value"]["rows"]

                atoms_sql = 'SELECT reference, "content.summary" FROM mrt_atoms ORDER BY reference'
                before = await rows(atoms_sql)
                self.assertTrue(before)
                ticket.write_text("---\nidentity: [invalid\n")
                failed = await _invoke(http, project, "query_rebuild", {"target": "all"})
                self.assertIn("error", failed, failed)
                self.assertEqual(before, await rows(atoms_sql))
                issues = await rows("SELECT source, relative_path, code, message FROM ops_ingestion_issues")
                matching = [row for row in issues if row[0] == "atom" and row[1] == ticket.relative_to(project).as_posix()]
                self.assertEqual(1, len(matching), issues)
                self.assertEqual("parse_error", matching[0][2])
                self.assertTrue(matching[0][3])

                ticket.unlink()
                rebuilt = await _invoke(http, project, "query_rebuild", {"target": "all"})
                self.assertIn("result", rebuilt, rebuilt)
                self.assertEqual(before, await rows(atoms_sql))
                self.assertEqual([], await rows("SELECT source, relative_path, code, message FROM ops_ingestion_issues WHERE source = 'atom'"))
