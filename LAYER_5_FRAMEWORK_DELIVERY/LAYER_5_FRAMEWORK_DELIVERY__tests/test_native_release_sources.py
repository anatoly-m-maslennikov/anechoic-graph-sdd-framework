"""Native release sources retain the selected migration groups."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION'),
               str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS'),
               str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC'),
               str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43')]
from release_support import LocalReleaseError, _native_release_sources

PREFIX = '.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES'
CORE = 'CA-SU-11_LAYER_1_CORE_META_MODEL'


class NativeReleaseSourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.control = self.root / '.anechoic_anechoic'
        self.control.mkdir()
        manifest = self.control / 'manifest.md'
        manifest.write_bytes(b'manifest')
        self.selection = SimpleNamespace(root=self.root, control_root=self.control,
                                         manifest_path=manifest, manifest_sha256=hashlib.sha256(b'manifest').hexdigest(),
                                         project_prefix='AN')
        self.aliases = self.control / '_migration/native-aliases.json'
        self.aliases.parent.mkdir()
        self.rows = [['CA-R-1@1', f'{PREFIX}/{CORE}/04_requirement/CA-R-1-old.md', 'AN-S-1@1']]
        self.write_aliases()
        self.source = self.control / 'LAYER_C9/__DES/AN-S-1-DES--current.md'
        self.carrier(self.source, 2)

    def write_aliases(self):
        self.aliases.write_text(json.dumps(self.rows))

    def carrier(self, path, version, status='active'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'''---
identity:
  atom_id: AN-S-1
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: {status}
  version: {version}
---
## Summary

Current.

## Claim

Current claim.
''')

    def test_maps_current_successor_and_ignores_historical_and_installed(self):
        self.rows.append(['CA-R-1@2-draft', f'{PREFIX}/{CORE}/04_requirement/000_draft/CA-R-1-draft.md', 'AN-S-1@2-draft'])
        self.write_aliases()
        self.carrier(self.control / '000_ANECHOIC_framework/AN-S-1-DES--copy.md', 2)
        self.assertEqual({Path(CORE) / '04_requirement' / self.source.name: self.source},
                         _native_release_sources(self.selection))

    def test_duplicate_active_id_is_refused(self):
        self.carrier(self.control / 'OTHER/DES/AN-S-1-DES--duplicate.md', 2)
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_duplicate_alias_is_refused(self):
        self.rows.append(self.rows[0])
        self.write_aliases()
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_missing_current_carrier_is_refused(self):
        self.rows.append(['CA-R-2@1', f'{PREFIX}/{CORE}/04_requirement/CA-R-2-old.md', 'AN-S-2@1'])
        self.write_aliases()
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def admit_retirement(self):
        self.rows.append(['CA-R-2@1', f'{PREFIX}/{CORE}/04_requirement/CA-R-2-old.md', 'AN-S-2@1'])
        self.write_aliases()
        archive = self.control / 'LAYER_C9/DES/099_archived/AN-S-2@2-DES--archived.md'
        self.carrier(archive, 2, status='archived')
        archive.write_text(archive.read_text().replace('AN-S-1', 'AN-S-2'))
        retirement = self.control / '_migration/native-archive-only.json'
        retirement.write_text(json.dumps([{'exact_ref': 'AN-S-2@2',
                                           'path': archive.relative_to(self.control).as_posix()}]))
        return archive, retirement

    def test_archive_only_identity_is_admitted(self):
        self.admit_retirement()
        self.assertEqual({Path(CORE) / '04_requirement' / self.source.name: self.source},
                         _native_release_sources(self.selection))

    def test_missing_or_unadmitted_archive_is_refused(self):
        archive, retirement = self.admit_retirement()
        retirement.unlink()
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)
        self.admit_retirement()
        archive.unlink()
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_current_and_retirement_conflict_is_refused(self):
        self.admit_retirement()
        current = self.control / 'LAYER_C9/DES/AN-S-2-DES--current.md'
        self.carrier(current, 3)
        current.write_text(current.read_text().replace('AN-S-1', 'AN-S-2'))
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_changed_retirement_inputs_are_refused(self):
        import release_support
        archive, retirement = self.admit_retirement()
        original = release_support._file_identity
        for target in (archive, retirement):
            counts = {}
            def changed(path):
                counts[path] = counts.get(path, 0) + 1
                identity = original(path)
                return ('0' * 64, identity[1]) if path == target and counts[path] > 1 else identity
            with self.subTest(target=target), patch.object(release_support, '_file_identity', side_effect=changed):
                with self.assertRaises(LocalReleaseError):
                    _native_release_sources(self.selection)

    def test_archive_symlink_swap_with_same_bytes_is_refused(self):
        import release_support
        archive, _ = self.admit_retirement()
        outside = self.root / 'outside.md'
        outside.write_bytes(archive.read_bytes())
        original = release_support._file_identity
        count = 0
        def swap(path):
            nonlocal count
            if path == archive:
                count += 1
                if count == 2:
                    archive.unlink()
                    archive.symlink_to(outside)
            return original(path)
        with patch.object(release_support, '_file_identity', side_effect=swap):
            with self.assertRaises(LocalReleaseError):
                _native_release_sources(self.selection)

    def test_changed_manifest_is_refused(self):
        self.selection.manifest_path.write_bytes(b'changed')
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_changed_source_is_refused(self):
        import release_support
        original = release_support._file_identity
        counts = {}
        def changed(path):
            counts[path] = counts.get(path, 0) + 1
            identity = original(path)
            return ('0' * 64, identity[1]) if path == self.source and counts[path] > 1 else identity
        with patch.object(release_support, '_file_identity', side_effect=changed):
            with self.assertRaises(LocalReleaseError):
                _native_release_sources(self.selection)


if __name__ == '__main__':
    unittest.main()
