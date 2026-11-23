"""Exercise watcher triggers through the Orchestrator and real Worker processes."""

import tempfile
import time
import unittest
from hashlib import sha256
from pathlib import Path

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
                (root / '.anechoic_tmp').mkdir()
                time.sleep(2.5)
                self.assertEqual(5, len(kernel.generations))
                self.assertEqual(['/generation'] * 5, kernel.paths)

    def test_real_process_observes_control_and_root_only(self):
        with tempfile.TemporaryDirectory(prefix='ane-watch-', dir='/tmp') as directory:
            root = Path(directory).resolve()
            ignored = root / 'ignored'
            ignored.mkdir()
            with watch_project(root) as (control, manifest, path, kernel, process):
                atom = self._write_atom(control, 'Task')
                self._await_delta(path, kernel, process, 2, root, atom)
                self._write_atom(control, 'Edited Task')
                self._await_delta(path, kernel, process, 3, root, atom)
                renamed = atom.rename(atom.with_name('AN-T-1--renamed.md'))
                self._await_delta(path, kernel, process, 4, root, atom, renamed)
                renamed.unlink()
                self._await_delta(path, kernel, process, 5, root, renamed)
                self.assertEqual([], kernel.payloads[-1]['snapshot']['atoms'])
                (ignored / 'ignored.md').write_text('ignored')
                time.sleep(2.5)
                self.assertEqual(['/generation'] + ['/generation/native-delta'] * 4, kernel.paths)
                manifest.write_text(manifest.read_text() + '\nchanged\n')
                wait_for(lambda: (latest(path) or {}).get('state') == 'failed', process)
                self.assertEqual(5, len(kernel.generations))

    def _await_delta(self, path, kernel, process, generation, root, *changed):
        wait_for(lambda: (latest(path) or {}).get('generation') == str(generation), process)
        self.assertEqual('native_delta', latest(path)['kind'])
        payload = kernel.payloads[-1]
        self.assertEqual({'instance_id', 'base_generation', 'paths', 'snapshot', 'snapshot_sha256', 'carrier_hashes'}, set(payload))
        self.assertEqual(str(generation - 1), payload['base_generation'])
        self.assertEqual([[item.parent.relative_to(root).as_posix(), item.name] for item in sorted(changed)],
                         payload['paths'])
        self.assertEqual({item.relative_to(root).as_posix(): sha256(item.read_bytes()).hexdigest()
                          for item in changed if item.exists()}, payload['carrier_hashes'])

    def test_stale_base_retries_full_and_other_rejections_discard_reuse(self):
        with tempfile.TemporaryDirectory(prefix='ane-watch-', dir='/tmp') as directory:
            root = Path(directory).resolve()
            with watch_project(root) as (control, _, path, kernel, process):
                kernel.delta_error = (409, 'delta_full_reconciliation')
                self._write_atom(control, 'Task')
                wait_for(lambda: (latest(path) or {}).get('generation') == '3', process)
                self.assertEqual(['/generation', '/generation/native-delta', '/generation/native'], kernel.paths)
                self.assertEqual('native_refresh', latest(path)['kind'])
                self.assertEqual('1', kernel.payloads[-1]['base_generation'])
                kernel.delta_error = (409, 'generation_base_changed')
                self._write_atom(control, 'Stale Task')
                wait_for(lambda: (latest(path) or {}).get('generation') == '5', process)
                self.assertEqual(['/generation/native-delta', '/generation'], kernel.paths[-2:])
                self.assertEqual('full', latest(path)['kind'])
                self._assert_full_proof(kernel.payloads[-1], 'Stale Task')
                kernel.delta_error = (409, 'another_error')
                self._write_atom(control, 'Rejected Task')
                wait_for(lambda: (latest(path) or {}).get('state') == 'failed', process)
                self.assertEqual(6, len(kernel.paths))
                self.assertEqual('5', kernel.payloads[-1]['base_generation'])
                kernel.delta_error = None
                self._write_atom(control, 'Recovered Task')
                wait_for(lambda: (latest(path) or {}).get('generation') == '7', process)
                self.assertEqual('/generation', kernel.paths[-1])
                self.assertEqual('full', latest(path)['kind'])
                self._assert_full_proof(kernel.payloads[-1], 'Recovered Task')

    def _assert_full_proof(self, payload, summary):
        self.assertNotIn('base_generation', payload)
        self.assertEqual({'inputs', 'graph_config', 'endpoints'}, set(payload['reuse']))
        summaries = {atom['reference']: atom['summary'] for atom in payload['snapshot']['atoms']}
        self.assertEqual({'AN-S-1': 'Anechoic', 'AN-T-1': summary}, summaries)

    def _write_atom(self, control, summary):
        atom = control / '__TKT' / 'AN-T-1--task.md'
        atom.write_text('---\natom_family: TKT\natom_id: AN-T-1\ncontainer: {component: C00}\n'
                        'priority: 2\ncontext: {template: task}\n'
                        "state: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}\n"
                        f'---\n\n## Summary\n\n{summary}\n')
        return atom


if __name__ == '__main__':
    unittest.main()
