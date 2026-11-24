"""Exercise watcher triggers and the Orchestrator's Kernel admission paths."""

from contextlib import redirect_stderr
import errno
from io import StringIO
import json
import tempfile
import time
import unittest
from hashlib import sha256
import os
from pathlib import Path
from threading import Event, Thread
from unittest.mock import patch

from watchdog.events import DirCreatedEvent, DirDeletedEvent

from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared import GenerationJobs
from ORCHESTRATOR_beta_C68.watcher import SourceWatcher
from ORCHESTRATOR_beta_C68.watcher_poll import PollComplete

from .ORCHESTRATOR_beta_C68__tests__shared import kernel_server, latest, project, wait_for, watch_project


class CaptureFenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / "control"
        self.control.mkdir()
        self.watcher = SourceWatcher(self.root, self.control, defer_archives=True)
        self.addCleanup(self.watcher.close)

    def test_fence_detects_restored_mtime_and_leaves_event_queued(self):
        carrier = self.control / "atom.md"
        carrier.write_text("before")
        self.watcher.start()
        epoch = self.watcher.capture_epoch(trace=True)
        self.assertIsNotNone(epoch)
        diagnostics = StringIO()
        with redirect_stderr(diagnostics):
            self.assertTrue(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32))
        self.assertEqual("", diagnostics.getvalue())
        before = carrier.stat()
        carrier.write_text("edited")
        os.utime(carrier, ns=(before.st_atime_ns, before.st_mtime_ns))
        with redirect_stderr(diagnostics):
            self.assertIs(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32), False)
        report = json.loads(diagnostics.getvalue())
        self.assertEqual(("watcher_fence_failed", "foreground", "source_changed", "WARNING", "a" * 32),
                         (report["code"], report["phase"], report["reason"], report["severity"], report["run_id"]))
        self.assertEqual({"kind": "modified", "path": "control/atom.md", "stat_fields": ["ctime_ns"]},
                         report["observation"])
        self.assertGreaterEqual(report["wait_ms"], 0)
        with patch.dict(os.environ, ANECHOIC_LOG_LEVEL="ERROR"), redirect_stderr(StringIO()) as filtered:
            self.assertIs(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32), False)
        self.assertEqual("", filtered.getvalue())
        self.assertIn(str(carrier), [change["old_path"] for change in self.watcher.changes(1)])

    def test_archive_baselines_are_separate_and_skip_installed_sources(self):
        archive = self.control / "09_archived"
        archive.mkdir()
        carrier = archive / "old.md"
        carrier.write_text("before")
        (self.control / "000_ANECHOIC_framework/09_archived").mkdir(parents=True)
        self.watcher.start()
        self.assertEqual(("control/09_archived",), self.watcher.archive_roots())
        self.assertIsNone(self.watcher.capture_epoch(archive=True))
        self.assertTrue(self.watcher.watch_archives())
        self.assertEqual([], self.watcher.changes(0.05))
        foreground = self.watcher.capture_epoch()
        background = self.watcher.capture_epoch(archive=True)
        carrier.unlink()
        self.assertIs(self.watcher.capture_fence(background, archive=True, timeout=3), False)
        self.assertTrue(self.watcher.capture_fence(foreground, timeout=3))
        self.assertIn(str(carrier), [change["old_path"] for change in self.watcher.changes(1)])
        new_root = self.control / "component" / "09_archived"
        new_root.mkdir(parents=True)
        self.assertIs(self.watcher.capture_fence(foreground, timeout=3), False)
        deadline = time.monotonic() + 3
        while "control/component/09_archived" not in self.watcher.archive_roots() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertIn("control/component/09_archived", self.watcher.archive_roots())

    def test_same_path_replacement_keeps_root_and_invalidates_intermediate_epoch(self):
        archive = self.control / "09_archived"
        archive.mkdir()
        replacement = self.root / "replacement"
        replacement.mkdir()
        self.watcher.start()
        self.assertTrue(self.watcher.watch_archives())
        roots = ("control/09_archived",)
        with self.watcher._proof.condition:
            archive.rename(self.root / "old")
            replacement.rename(archive)
            self.watcher.dispatch(DirDeletedEvent(str(archive)))
            self.watcher.dispatch(DirCreatedEvent(str(archive)))
            self.assertEqual(roots, self.watcher.archive_roots())
            epoch = self.watcher.capture_epoch(archive=True)
            self.assertIsNotNone(epoch)
            info = archive.stat()
            self.watcher.on_poll_complete(PollComplete(str(self.control), started=time.monotonic_ns(), clean=True,
                                                       archive=True, roots=((roots[0], info.st_ino, info.st_dev),)))
            self.assertIs(self.watcher.capture_fence(epoch, archive=True, timeout=0), False)
            self.assertEqual(roots, self.watcher.archive_roots())

    def test_completed_archive_scope_replaces_roots_when_parent_moves(self):
        component = self.control / "component"
        (component / "09_archived").mkdir(parents=True)
        self.watcher.start()
        self.assertTrue(self.watcher.watch_archives())
        epoch = self.watcher.capture_epoch(archive=True)
        component.rename(self.control / "moved")
        self.assertIsNot(self.watcher.capture_fence(epoch, archive=True, timeout=3), True)
        condition = self.watcher._proof.condition
        with condition:
            self.assertTrue(condition.wait_for(
                lambda: self.watcher.archive_roots() == ("control/moved/09_archived",), timeout=3))

    def test_close_releases_waiting_fence(self):
        self.watcher.start()
        epoch = self.watcher.capture_epoch()
        started, finished = Event(), Event()
        results = []

        def fence():
            started.set()
            results.append(self.watcher.capture_fence(epoch, timeout=3))
            finished.set()

        thread = Thread(target=fence)
        thread.start()
        self.assertTrue(started.wait(1))
        self.watcher.close()
        self.assertTrue(finished.wait(1))
        thread.join()
        self.assertEqual([None], results)

    def test_fence_refuses_an_incomplete_poll(self):
        carrier = self.control / "atom.md"
        carrier.write_text("present")
        self.watcher.start()
        epoch = self.watcher.capture_epoch(trace=True)
        lstat = os.lstat

        def denied(path, *args, **kwargs):
            if path == str(carrier):
                raise PermissionError(errno.EACCES, "private exception text", path)
            return lstat(path, *args, **kwargs)

        diagnostics = StringIO()
        with patch("ORCHESTRATOR_beta_C68.watcher_poll.os.lstat", side_effect=denied), redirect_stderr(diagnostics):
            self.assertIsNone(self.watcher.capture_fence(epoch, timeout=3, run_id="a" * 32))
        report = json.loads(diagnostics.getvalue())
        self.assertEqual("coverage_lost", report["reason"])
        self.assertEqual({"kind": "lstat_failed", "path": "control/atom.md", "errno": errno.EACCES}, report["observation"])
        self.assertNotIn("private exception text", diagnostics.getvalue())
        self.assertNotIn(str(self.root), diagnostics.getvalue())

    def test_native_ticket_start_defers_archive_index_and_runs_once(self):
        tickets = self.control / "__TKT"
        archive = tickets / "09_archived"
        archive.mkdir(parents=True)
        (archive / "archive.md").touch()
        carrier = tickets / "live.md"
        carrier.touch()
        with patch("ORCHESTRATOR_beta_C68.watcher.Observer") as observer:
            self.watcher.start()
            observer.assert_not_called()
            with patch.object(self.watcher, "_ticket_version", wraps=self.watcher._ticket_version) as version:
                self.watcher.start_ticket_watch()
                self.watcher.start_ticket_watch()
            observer.assert_called_once()
            version.assert_called_once_with(carrier)
            self.assertEqual(("created", [carrier]), self.watcher._ticket_change("created", [carrier]))
            self.assertIsNone(self.watcher._ticket_change("created", [carrier]))


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
        directory = self.enterContext(tempfile.TemporaryDirectory(prefix='ane-reconcile-', dir='/tmp'))
        root = Path(directory).resolve()
        control, manifest = project(root)
        (control / '__TKT').mkdir()
        binding = {'root': str(root), 'control_root': control.name, 'manifest_path': manifest.name,
                   'manifest_sha256': sha256(manifest.read_bytes()).hexdigest(), 'project_prefix': 'AN'}
        kernel = self.enterContext(kernel_server(root))
        jobs = GenerationJobs('test', binding, str(root / 'kernel.sock'))
        self.enterContext(patch.object(jobs, '_communicate_worker', side_effect=self._fixture_worker))
        jobs.startup_capture = True
        jobs._generate(startup=True)
        self._assert_stage(jobs, kernel, 0, 'full', '1', [('/generation', None)])

        delta = '/generation/native-delta'
        stages = (
            ('Task', 'delta_full_reconciliation', 'native_refresh', '3', [(delta, '1'), ('/generation/native', '1')]),
            ('Stale Task', 'generation_base_changed', 'full', '5', [(delta, '3'), ('/generation', None)]),
            ('Rejected Task', 'another_error', None, None, [(delta, '5')]),
            ('Recovered Task', None, 'full', '7', [('/generation', None)]),
        )
        for summary, reject, kind, generation, routes in stages:
            with self.subTest(stage=summary):
                previous = len(kernel.paths)
                kernel.delta_error = (409, reject) if reject else None
                atom = self._write_atom(control, summary)
                change = {'old_path': str(atom), 'new_path': None, 'event_type': 'modified', 'is_directory': False}
                jobs._generate(changes=[change])
                self._assert_stage(jobs, kernel, previous, kind, generation, routes)
                if kind == 'full':
                    self._assert_full_proof(kernel.payloads[-1], summary)
                if reject == 'another_error':
                    self.assertIsNone(jobs.generation_reuse)
                    self.assertIn(reject, jobs.status()['latest']['message'])

    def _assert_stage(self, jobs, kernel, previous, kind, generation, routes):
        latest_run = jobs.status()['latest'] or {}
        actual_routes = [(path, payload.get('base_generation'))
                         for path, payload in zip(kernel.paths[previous:], kernel.payloads[previous:])]
        detail = f'latest={latest_run!r}, Kernel routes={kernel.paths!r}'
        expected_state = 'succeeded' if generation is not None else 'failed'
        self.assertEqual((expected_state, kind, generation),
                         (latest_run.get('state'), latest_run.get('kind'), latest_run.get('generation')), detail)
        self.assertEqual(routes, actual_routes, detail)

    @staticmethod
    def _fixture_worker(directory, request):
        binding = request['binding']
        ticket = Path(binding['control_root']) / '__TKT/AN-T-1--task.md'
        carrier = Path(binding['root']) / ticket
        atoms, hashes = [], {}
        if carrier.exists():
            raw = carrier.read_bytes()
            atoms.append({'reference': 'AN-T-1', 'summary': raw.decode().split('## Summary\n\n')[1].strip()})
            hashes[ticket.as_posix()] = sha256(raw).hexdigest()
        paths, reuse = request.get('paths'), request['reuse']
        if paths is None:
            atoms.insert(0, {'reference': 'AN-S-1', 'summary': 'Anechoic'})
        snapshot = {'atoms': atoms}
        result = {'snapshot': snapshot, 'carrier_hashes': hashes}
        if reuse is None:
            for name in ('model.json', 'structure.json'):
                (Path(directory) / name).write_text('{}')
            witness = {'inputs': {'manifest': 'fixture'}, 'graph_config': None, 'endpoints': {}}
            result.update(receipt={}, graph=None, reuse=witness)
            if request.get('foreground'):
                result['deferred_archive'] = {'roots': [], 'snapshot': {'atoms': []},
                                              'carrier_hashes': {}, 'endpoints': {}}
        else:
            if paths is not None:
                result['paths'] = [[Path(path).parent.as_posix(), Path(path).name] for path in paths]
            digest_input = result if paths is not None else snapshot
            digest = sha256(json.dumps(digest_input, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
            result.update(base_generation=reuse['base_generation'], snapshot_sha256=digest.hexdigest())
        return json.dumps(result)

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
