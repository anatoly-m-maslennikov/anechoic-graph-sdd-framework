"""Small regression tests for untrusted carriers and read boundaries."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from io import BytesIO
import os
from pathlib import Path
import sys
import tempfile
from threading import Event
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (  # noqa: E402
    CarrierError,
    LimitReached,
    ReadContext,
    ReadFailure,
    frontmatter_bounds,
    parse_carrier,
    source_body,
)  # fmt: skip


class CarrierTests(unittest.TestCase):
    def test_body_adapter_uses_search_position_and_preserves_error(self):
        raw = b"---\r\n---\r\n\xffbody"
        self.assertEqual((5, 4, 10), frontmatter_bounds(raw))
        self.assertEqual(b"\xffbody", source_body(raw, Path("case.md")))
        with self.assertRaisesRegex(
            ValueError, "case.md: unsupported frontmatter delimiter"
        ):
            source_body(b"plain", Path("case.md"))

    def test_valid_and_no_identity_inference(self) -> None:
        parsed = parse_carrier(
            b"---\nstatus: Active\n---\n# Summary\n\nHi\n",
            Path("/CA-R-001.md"),
        )
        self.assertEqual(parsed._view["status"], "Active")
        self.assertEqual(parsed.metadata, {"status": "Active"})
        self.assertNotIn("atom_id", parsed.metadata)

    def test_duplicate_nested_key(self) -> None:
        with self.assertRaises(CarrierError) as caught:
            parse_carrier(
                b"---\nsubjects: {governs: A, governs: B}\n---\nx",
                Path("/a.md"),
            )
        self.assertEqual(caught.exception.code, "YAML_DUPLICATE_KEY")

    def test_unsafe_tag(self) -> None:
        with self.assertRaises(CarrierError):
            parse_carrier(
                b'---\nx: !!python/object/apply:os.system ["exit 0"]\n---\nx',
                Path("/a.md"),
            )

    def test_alias_is_explicitly_unsupported(self) -> None:
        with self.assertRaises(CarrierError) as caught:
            parse_carrier(b"---\na: &a [*a]\n---\nx", Path("/a.md"))
        self.assertEqual(caught.exception.code, "YAML_UNSUPPORTED")

    def test_invalid_utf8(self) -> None:
        with self.assertRaises(CarrierError):
            parse_carrier(b"\xff", Path("/a.md"))

    def test_deep_yaml_is_bounded(self) -> None:
        data = b"---\nx: " + b"[" * 100 + b"0" + b"]" * 100 + b"\n---\nx"
        with self.assertRaises(CarrierError) as caught:
            parse_carrier(data, Path("/a.md"))
        self.assertEqual(caught.exception.code, "YAML_UNSUPPORTED")


class ReadTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = HERE.parents[4] / ".anechoic_tmp"
        parent.mkdir(exist_ok=True)
        self.root = Path(
            tempfile.mkdtemp(dir=parent, prefix="validator-input-test-")
        )
        self.limits = dict(
            max_candidates=10,
            max_file_bytes=20,
            max_total_read_bytes=40,
            timeout_seconds=30,
            max_findings=100,
        )
        self.reader = ReadContext([str(self.root)], self.limits)

    def test_denied_secret_without_content_read(self) -> None:
        with self.assertRaises(ReadFailure):
            self.reader.read(self.root / ".env")
        self.assertEqual(self.reader.bytes_read, 0)

    def test_outside_root(self) -> None:
        with self.assertRaises(ReadFailure):
            self.reader.read(Path("/etc/hosts"))

    def test_budget_and_currentness(self) -> None:
        path = self.root / "a.md"
        path.write_bytes(b"original")
        self.reader.read(path)
        path.write_bytes(b"changed")
        self.assertEqual(self.reader.currentness()["state"], "changed")
        path.write_bytes(b"x" * 21)
        with self.assertRaises(LimitReached):
            self.reader.read(path)

    def test_test_image_deadline_switch_keeps_file_byte_limit(self) -> None:
        switch = "ANECHOIC_TEST_IMAGE_DEADLINES"
        self.reader.started -= self.limits["timeout_seconds"]
        path = self.root / "input.md"
        path.write_bytes(b"x" * (self.limits["max_file_bytes"] + 1))
        with patch.dict(os.environ):
            os.environ.pop(switch, None)
            with self.assertRaisesRegex(LimitReached, "timeout_seconds"):
                self.reader.read(path)
            os.environ[switch] = "1"
            with self.assertRaisesRegex(LimitReached, "timeout_seconds"):
                self.reader.read(path)
            os.environ[switch] = "0"
            with self.assertRaisesRegex(LimitReached, "max_file_bytes"):
                self.reader.read(path)

    def test_parallel_reads_share_total_byte_budget(self) -> None:
        self.limits["max_total_read_bytes"] = 20
        started, release = Event(), Event()

        class BlockedRead(BytesIO):
            def read(self, size):
                started.set()
                if not release.wait(5):
                    raise AssertionError("Test read was not released")
                return super().read(size)

        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(
                self.reader._read_bytes, BlockedRead(b"x" * 11), 11
            )
            try:
                self.assertTrue(started.wait(5))
                with self.assertRaisesRegex(
                    LimitReached, "max_total_read_bytes"
                ):
                    self.reader._read_bytes(BytesIO(b"y" * 11), 11)
            finally:
                release.set()
            self.assertEqual(first.result(), b"x" * 11)
        self.assertEqual(self.reader.bytes_read, 11)

    def test_inventory_rechecks_entry_type_when_it_visits_the_path(
        self,
    ) -> None:
        entry = self.root / "pending"
        entry.touch()
        self.assertEqual(self.reader.inventory(self.root), [])
        scandir = os.scandir

        @contextmanager
        def scan_and_replace(descriptor):
            with scandir(descriptor) as entries:
                yield entries
            if entry.is_file():
                entry.unlink()
                entry.mkdir()
                (entry / "a.md").write_text("new input", encoding="utf-8")

        with patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30_"
                "_pub.os.scandir"
            ),
            scan_and_replace,
        ):
            self.assertEqual(self.reader.currentness()["state"], "changed")

    def test_symlink_escape(self) -> None:
        path = self.root / "outside.md"
        path.symlink_to("/etc/hosts")
        with self.assertRaises(ReadFailure):
            self.reader.read(path)

    def test_read_rejects_symlinked_parent(self) -> None:
        target = self.root / "target"
        target.mkdir()
        (target / "a.md").write_bytes(b"input")
        alias = self.root / "alias"
        alias.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ReadFailure):
            self.reader.read(alias / "a.md")
        self.assertEqual(self.reader.bytes_read, 0)

    def test_inventory_checks_metadata_guard_without_rereading(self) -> None:
        path = self.root / "a.md"
        path.write_bytes(b"original")
        self.reader.inventory(self.root)
        self.reader.read(path, metadata_guard=True)
        original = path.stat()
        self.assertEqual(self.reader.currentness()["state"], "unchanged")
        path.write_bytes(b"modified")
        os.utime(path, ns=(original.st_atime_ns, original.st_mtime_ns))
        self.assertEqual(self.reader.currentness()["state"], "changed")
        self.assertEqual(self.reader.bytes_read, len(b"original"))

    def test_metadata_guard_rejects_replaced_parent_with_same_file(
        self,
    ) -> None:
        directory = self.root / "source"
        directory.mkdir()
        path = directory / "a.md"
        path.write_bytes(b"original")
        self.reader.inventory(self.root)
        self.reader.read(path, metadata_guard=True)
        moved = directory.rename(self.root / "moved")
        directory.symlink_to(moved, target_is_directory=True)
        self.assertIn(
            {"path": str(path)}, self.reader.currentness()["affected_inputs"]
        )


if __name__ == "__main__":
    unittest.main()
