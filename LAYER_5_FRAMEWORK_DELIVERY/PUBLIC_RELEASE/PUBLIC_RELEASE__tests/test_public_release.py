import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from public_release import PublicReleaseError, run_public_release


class PublicReleaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'user.name', 'Test')
        (self.root / 'version.toml').write_text('[framework]\nversion = "1.2.3"\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        (self.root / 'version.toml').write_text('[framework]\nversion = "1.2.4"\n')
        self.tickets = self.root / '_anechoic_anechoic/001_TICKETS/TASKS'
        self.tickets.mkdir(parents=True)
        (self.tickets / 'AN-T-1-TASK--done.md').write_text('---\natom_id: AN-T-1\ncontext:\n  template: task\nstate:\n  status: "done"\n---\n# Summary\n\nDone task\n')
        (self.tickets / 'AN-T-2-EPIC--open.md').write_text('---\natom_id: AN-T-2\ncontext:\n  template: epic\nstate:\n  status: active\n---\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'head')
        self.head = self.git('rev-parse', 'HEAD')
        self.addCleanup(self.tmp.cleanup)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()

    def run_release(self, **kwargs):
        return run_public_release(self.root, run_id='test', base_ref=self.base, head_ref=self.head, **kwargs)

    def test_comparison_and_rendering_are_read_only(self):
        before = self.git('status', '--porcelain')
        result = self.run_release()
        self.assertEqual(result['outcome'], 'input_required')
        self.assertEqual(result['version'], '1.2.4')
        self.assertEqual(result['merge_base'], self.base)
        self.assertEqual(result['diff_argv'], ['git', 'diff', '--find-renames', self.base, self.head, '--'])
        self.assertEqual([ticket['path'] for ticket in result['completed_tickets']], ['_anechoic_anechoic/001_TICKETS/TASKS/AN-T-1-TASK--done.md'])
        draft = {'base_commit': self.base, 'head_commit': self.head, 'changes': [{'title': 'Add feature', 'details': 'Adds a feature.', 'evidence': ['AN-T-1'], 'highlight': True}]}
        rendered = self.run_release(content_draft=draft)
        self.assertIn('Adds a feature.', rendered['pr_description'])
        self.assertEqual(rendered['version_history_entry'], '## 1.2.4\n\n- Add feature\n')
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
        self.assertEqual(len(self.run_release()['completed_tickets']), 1)
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
