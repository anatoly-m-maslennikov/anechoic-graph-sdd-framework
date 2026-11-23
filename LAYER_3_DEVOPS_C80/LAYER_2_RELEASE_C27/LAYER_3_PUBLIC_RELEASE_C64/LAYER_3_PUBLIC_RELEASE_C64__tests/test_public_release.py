import json
import tempfile
import unittest
from pathlib import Path

from LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__shared import PublicReleaseError
from LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__tests.LAYER_3_PUBLIC_RELEASE_C64__tests__shared import PublicReleaseFixture


class PublicReleaseTest(PublicReleaseFixture, unittest.TestCase):
    def test_comparison_and_rendering_are_read_only(self):
        before = self.git('status', '--porcelain')
        code, result = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(result['outcome'], 'input_required')
        self.assertEqual((result['base_commit'], result['head_commit']), (self.base, self.head))
        self.assertEqual(result['version'], '1.2.4')
        self.assertEqual(result['merge_base'], self.base)
        self.assertIn('Luna', result['instructions'])
        self.assertEqual((result['content_draft_schema']['base_commit'], result['content_draft_schema']['head_commit']), (self.base, self.head))
        self.assertEqual(result['diff_argv'], ['git', 'diff', '--find-renames', self.base, self.head, '--'])
        self.assertEqual({ticket['path'] for ticket in result['completed_tickets']}, {
            f'_anechoic_anechoic/{branch}/TASKS/AN-T-{number}-TASK--done.md'
            for branch, number in (('001_TICKETS', 1), ('__TICKETS', 3), ('__TKT', 4))})
        draft = {'base_commit': self.base, 'head_commit': self.head, 'changes': [{'title': 'Add feature', 'details': 'Adds a feature.', 'evidence': ['AN-T-1'], 'highlight': True}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'draft.json'
            payload = json.dumps(draft).encode('utf-8')
            path.write_bytes(payload)
            code, rendered = self.run_cli('--content-draft', str(path))
            self.assertEqual(code, 0)
            self.assertEqual(rendered['outcome'], 'completed')
            self.assertIn('Adds a feature.', rendered['pr_description'])
            self.assertEqual(rendered['version_history_entry'], '## 1.2.4\n\n- Add feature\n')
            self.assertEqual(path.read_bytes(), payload)
            draft['head_commit'] = 'bad'
            path.write_text(json.dumps(draft), encoding='utf-8')
            code, rejected = self.run_cli('--content-draft', str(path))
            self.assertEqual(code, 1)
            self.assertEqual((rejected['outcome'], rejected['failed_step']), ('failed', 'changelog'))
            self.assertIn('commit pins', rejected['error'])
        self.assertEqual(self.git('status', '--porcelain'), before)

    def test_rejects_stale_pins_and_invalid_entries(self):
        draft = {'base_commit': self.base, 'head_commit': 'bad', 'changes': []}
        with self.assertRaises(PublicReleaseError):
            self.run_release(content_draft=draft)
        draft['head_commit'] = self.head
        with self.assertRaises(PublicReleaseError):
            self.run_release(content_draft=draft)
        draft['changes'] = [{'title': 'Feature', 'details': 'Details', 'evidence': [], 'highlight': True}]
        with self.assertRaises(PublicReleaseError):
            self.run_release(content_draft=draft)


    def test_excludes_archives_snapshots_and_symlinks_and_rejects_duplicates(self):
        done = (self.tickets / 'AN-T-1-TASK--done.md').read_text()
        for folder in ('09_archived', 'snapshot'):
            (self.tickets / folder).mkdir()
            (self.tickets / folder / 'AN-T-1-TASK--copy.md').write_text(done)
        (self.tickets / 'AN-T-3-TASK--link.md').symlink_to('AN-T-1-TASK--done.md')
        self.git('add', '.')
        self.git('commit', '-qm', 'lookalikes')
        self.head = self.git('rev-parse', 'HEAD')
        self.assertEqual(len(self.run_release()['completed_tickets']), 3)
        (self.tickets / 'AN-T-1-TASK--duplicate.md').write_text(done)
        self.git('add', '.')
        self.git('commit', '-qm', 'duplicate')
        self.head = self.git('rev-parse', 'HEAD')
        with self.assertRaisesRegex(PublicReleaseError, 'duplicate'):
            self.run_release()

    def test_highlight_limits(self):
        change = {'title': 'Feature', 'details': 'Details', 'evidence': ['file'], 'highlight': True}
        draft = {'base_commit': self.base, 'head_commit': self.head, 'changes': [change.copy() for _ in range(6)]}
        with self.assertRaises(PublicReleaseError):
            self.run_release(content_draft=draft)
        draft['changes'][0]['highlight'] = False
        self.assertEqual(self.run_release(content_draft=draft)['version_history_entry'].count('- Feature'), 5)
        draft['changes'][1]['title'] = 'x' * 121
        with self.assertRaises(PublicReleaseError):
            self.run_release(content_draft=draft)


if __name__ == '__main__':
    unittest.main()
