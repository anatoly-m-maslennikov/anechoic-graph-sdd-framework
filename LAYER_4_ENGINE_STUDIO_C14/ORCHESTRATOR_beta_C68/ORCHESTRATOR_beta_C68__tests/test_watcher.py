"""Exercise watcher triggers through the Orchestrator and real Worker processes."""

from pathlib import Path
import tempfile
import time
import unittest

from .ORCHESTRATOR_beta_C68__tests__shared import latest, wait_for, watch_project


class WatcherTests(unittest.TestCase):
    def test_code_watch_triggers_and_exclusions(self):
        with tempfile.TemporaryDirectory(prefix='ane-code-', dir='/tmp') as directory:
            root = Path(directory).resolve()
            source, excluded = root / 'src', root / 'generated'
            source.mkdir()
            excluded.mkdir()
            script, renamed = source / 'main.py', source / 'renamed.py'
            with watch_project(root, watch_code=True) as (_, _, path, kernel, process):
                def await_generation(generation):
                    wait_for(lambda: (latest(path) or {}).get('generation') == str(generation), process)

                script.write_text('print(1)')
                await_generation(2)
                script.rename(renamed)
                await_generation(3)
                renamed.unlink()
                await_generation(4)
                (root / 'uv.lock').write_text('version = 1\n')
                await_generation(5)
                (excluded / 'ignored.py').write_text('ignored')
                time.sleep(2.5)
                self.assertEqual(5, len(kernel.generations))

    def test_real_process_observes_control_and_root_only(self):
        with tempfile.TemporaryDirectory(prefix='ane-watch-', dir='/tmp') as directory:
            root = Path(directory).resolve()
            ignored = root / 'ignored'
            ignored.mkdir()
            with watch_project(root) as (control, manifest, path, kernel, process):
                (ignored / 'ignored.md').write_text('ignored')
                time.sleep(2.5)
                self.assertEqual(1, len(kernel.generations))
                (control / '__TKT').mkdir()
                (control / '__TKT' / 'AN-T-1-task.md').write_text(
                    '---\nidentity:\n  atom_id: AN-T-1\ncontext:\n  container:\n    component: C0\n'
                    'state:\n  status: active\n  version: 1\n---\n\n## Summary\n\nTask\n')
                wait_for(lambda: (latest(path) or {}).get('generation') == '2', process)
                manifest.write_text(manifest.read_text() + '\nchanged\n')
                wait_for(lambda: (latest(path) or {}).get('state') == 'failed', process)
                self.assertEqual(2, len(kernel.generations))


if __name__ == '__main__':
    unittest.main()
