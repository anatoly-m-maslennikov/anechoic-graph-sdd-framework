"""Verify passive Release selection and its filesystem boundary."""

from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import release_inputs


class ReleaseInputsTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def manifest(self, *, control=".anechoic_anechoic", flat=False, parameters=None):
        folder = self.root / control
        folder.mkdir(exist_ok=True)
        path = folder / "AN-S-001-PROJECT_MANIFEST--declare.md"
        header = ("atom_family: SPEC\natom_id: AN-S-001\ncontainer:\n  component: C00\ntier: -1\n"
                  "context:\n  template: project_manifest\n" if flat else
                  "identity:\n  atom_id: AN-S-001\ncontext:\n  container:\n    component: C00\n"
                  "  tier: -1\n  template: project_manifest\n")
        path.write_text(
            f"---\n{header}state:\n  status: active\n  version: 1\n---\n"
            "## Claim\n\n### Formal Claim\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            "declare_entity(entity_name='Project Manifest', instance=ProjectManifest("
            f"name='Anechoic', prefix='AN', parameters={parameters or {'project_mcp': {'http_port': 56317}}!r}))\n"
            "```\n", encoding="utf-8")
        return path

    def test_flat_and_nested_headers_and_exact_identity(self):
        path = self.manifest()
        for flat in (False, True):
            if flat:
                self.manifest(flat=True)
            selected = release_inputs.read_release_selection(self.root)
            self.assertEqual(selected, release_inputs.read_release_selection(self.root, ".anechoic_anechoic"))
            self.assertEqual("AN-S-001@1", selected.manifest_ref)
            self.assertEqual(56317, selected.parameters["project_mcp"]["http_port"])
            self.assertEqual(sha256(path.read_bytes()).hexdigest(), selected.manifest_sha256)
            expected = sha256(f"{self.root}\0.anechoic_anechoic".encode()).hexdigest()
            self.assertEqual(expected, selected.instance_id)
            self.assertEqual(self.root / ".anechoic_runtime/runtime/project_mcp" / expected, selected.launcher_state)

    def test_real_project_manifest(self):
        root = Path(__file__).resolve().parents[3]
        selected = release_inputs.read_release_selection(root)
        self.assertEqual("Anechoic", selected.project_name)
        self.assertEqual("AN", selected.project_prefix)
        self.assertEqual(56317, selected.parameters["project_mcp"]["http_port"])

    def test_release_port_is_left_for_the_callers_existing_validation(self):
        for value in (False, 0, 65536, "56317"):
            with self.subTest(port=value):
                self.manifest(parameters={"project_mcp": {"http_port": value}})
                selection = release_inputs.read_release_selection(self.root)
                self.assertIs(type(selection.parameters["project_mcp"]["http_port"]), type(value))
                self.assertEqual(value, selection.parameters["project_mcp"]["http_port"])

    def test_copy_gets_its_own_bound_instance_id(self):
        source = self.manifest()
        original = release_inputs.read_release_selection(self.root)
        copied_root = self.root / "copy"
        copied_control = copied_root / original.control_relative
        copied_control.mkdir(parents=True)
        (copied_control / source.name).write_bytes(source.read_bytes())
        copied = release_inputs.read_release_selection(copied_root, original.control_relative)
        self.assertEqual(original.manifest_sha256, copied.manifest_sha256)
        self.assertNotEqual(original.instance_id, copied.instance_id)
        self.assertEqual(sha256(f"{copied_root}\0.anechoic_anechoic".encode()).hexdigest(), copied.instance_id)

    def test_control_ambiguity_and_symlinks_are_refused(self):
        self.manifest()
        self.manifest(control="_anechoic_anechoic")
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root)
        (self.root / "_anechoic_anechoic" / "AN-S-001-PROJECT_MANIFEST--declare.md").unlink()
        (self.root / "_anechoic_anechoic").rmdir()
        (self.root / "_anechoic_anechoic").symlink_to(self.root / ".anechoic_anechoic")
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root)
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root, "_anechoic_anechoic")
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root, "../.anechoic_anechoic")

    def test_rejects_unsafe_claim_and_conflicting_identity(self):
        path = self.manifest()
        source = path.read_text(encoding="utf-8")
        for original, replacement in (
            ("56317", "__import__('os').system('false')"),
            ("prefix='AN'", "prefix='OTHER'"),
            ("component: C00", "component: C01"),
            ("status: active", "status: draft"),
            ("version: 1", "version: 1\n  version: 2"),
        ):
            with self.subTest(replacement=replacement):
                path.write_text(source.replace(original, replacement), encoding="utf-8")
                with self.assertRaises(ValueError):
                    release_inputs.read_release_selection(self.root)

    def test_control_prefix_and_declared_control_are_checked(self):
        self.manifest(parameters={"project_mcp": {"http_port": 56317},
                                  "project": {"root": {"prefix": "underscore"}}})
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root)
        self.manifest(parameters={"project_mcp": {"http_port": 56317},
                                  "paths": {"control_root": "other"}})
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root)

    def test_changed_manifest_during_selection_is_refused(self):
        path = self.manifest()
        original = release_inputs._read
        calls = 0

        def change(fd, name):
            nonlocal calls
            calls += 1
            if calls == 2:
                path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
            return original(fd, name)

        with patch.object(release_inputs, "_read", side_effect=change), self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root)

    def test_file_symlink_and_symlink_root_are_refused(self):
        path = self.manifest()
        actual = self.root / "manifest.txt"
        path.rename(actual)
        path.symlink_to(actual)
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(self.root)
        alias = self.root.parent / (self.root.name + "-alias")
        alias.symlink_to(self.root)
        self.addCleanup(alias.unlink)
        with self.assertRaises(ValueError):
            release_inputs.read_release_selection(alias)


if __name__ == "__main__":
    unittest.main()
