"""Verify staged startup and persisted offline reconciliation in the candidate image."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import tempfile
from time import monotonic
import unittest

from mcp.client.session import ClientSession

from ..workbench_docker_support import image_mcp_transport, image_timeout, request
from .staged_startup__support import PackagedProbe, prepare


def query(ref):
    return ('SELECT relative_path, filename, "content.summary" FROM atoms '
            f"WHERE reference='{ref}'")


def status_counts(probe):
    return dict(probe.rows('SELECT status_group, count(*) FROM atoms GROUP BY 1'))


def public_ready(probe):
    status, payload = request(probe.url + '/anechoic/health')
    return status == 200 and isinstance(payload, dict) and payload.get('ready') is True


def paths(directory):
    return [directory / f'AN-T-{i}-TASK--staged.md' for i in range(1, 5)]


class PackagedStagedStartupTests(unittest.TestCase):
    def test_staged_startup_and_disk_restart(self):
        image = os.environ.get('ANECHOIC_IMAGE', '')
        self.assertRegex(image, r'\Asha256:[0-9a-f]{64}\Z')
        environment = subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{json .Config.Env}}', image],
                                              text=True, timeout=image_timeout(10))
        if 'ANECHOIC_RUNTIME_STACK=beta' not in json.loads(environment):
            self.skipTest('Staged startup applies to the Beta runtime')
        temp = self.enterContext(tempfile.TemporaryDirectory(prefix='anechoic-staged-image-'))
        root = Path(temp).resolve()
        subprocess.run(['git', 'init', '--quiet', str(root)], check=True, timeout=image_timeout(10))
        directory = prepare(root)
        probe = PackagedProbe(self, root, image)
        try:
            self._exercise(probe, directory)
        except BaseException:
            logs = probe.docker('logs', probe.container, timeout=30)
            print(logs[-12000:], flush=True)
            raise

    def _exercise(self, probe, directory):
        files = paths(directory)
        probe.until(probe.stopped, 'archive Worker barrier')
        health, _ = probe.until(probe.ready, 'foreground readiness')
        metrics = {'cold_ready_seconds': monotonic() - probe.started}
        self.assertTrue(health['archive_pending'])
        self.assertEqual(0, status_counts(probe).get('Archived', 0))
        probe.until(lambda: public_ready(probe), 'public health')
        asyncio.run(self._mcp_query(probe.url))
        files[0].write_text(files[0].read_text().replace('Current 1', 'Live edit 1'))
        parent = directory.relative_to(probe.root).as_posix()
        expected = [[parent, files[0].name, 'Live edit 1']]
        probe.until(lambda: probe.rows(query('AN-T-1')) == expected, 'live edit publication')
        self.assertTrue(probe.health()['archive_pending'])
        probe.release()
        probe.until(probe.complete, 'archive completion')
        metrics['cold_archive_complete_seconds'] = monotonic() - probe.started
        self.assertEqual(expected, probe.rows(query('AN-T-1')))
        before = status_counts(probe)
        self.assertEqual(1500, before.get('Archived'))
        disk = probe.disk()
        probe.docker('stop', '--time', '30', probe.container, timeout=60)
        files[1].write_text(files[1].read_text().replace('Current 2', 'Offline edit 2'))
        moved = files[2].with_name('AN-T-3-TASK--staged-moved.md')
        files[2].rename(moved)
        files[3].unlink()
        restart_started = monotonic()
        probe.docker('start', probe.container, timeout=60)
        probe.refresh_binding('restart')
        self._check_restart(probe, parent, files, moved, expected, disk, before, metrics, restart_started)
        print('ANECHOIC_TEST_METRICS ' + json.dumps({'staged_startup': metrics}), flush=True)

    def _check_restart(self, probe, parent, files, moved, live, disk, before, metrics, restart_started):
        pid = probe.until(probe.stopped, 'restart archive Worker barrier')
        probe.phase('restart_archive_paused', worker_pid=pid)
        health, _ = probe.until(probe.ready, 'restart foreground readiness')
        metrics['restored_ready_seconds'] = monotonic() - restart_started
        self.assertTrue(health['archive_pending'])
        probe.phase('restart_foreground_ready', generation=health['generation'])
        self.assertEqual([[parent, files[1].name, 'Offline edit 2']], probe.rows(query('AN-T-2')))
        self.assertEqual([[parent, moved.name, 'Current 3']], probe.rows(query('AN-T-3')))
        self.assertEqual([], probe.rows(query('AN-T-4')))
        self.assertEqual(live, probe.rows(query('AN-T-1')))
        self.assertEqual(disk, probe.disk())
        probe.phase('restart_offline_rows_verified')
        probe.until(lambda: public_ready(probe), 'restart public health')
        probe.phase('restart_public_ready', url=probe.url)
        asyncio.run(self._mcp_query(probe.url))
        probe.phase('restart_mcp_query_passed')
        files[0].write_text(files[0].read_text().replace('Live edit 1', 'Restart live edit 1'))
        probe.phase('restart_live_edit_written')
        restarted = [[parent, files[0].name, 'Restart live edit 1']]
        probe.until(lambda: probe.rows(query('AN-T-1')) == restarted, 'restart live edit')
        probe.phase('restart_live_edit_observed')
        self.assertTrue(probe.health()['archive_pending'])
        probe.release()
        probe.until(probe.complete, 'restart archive completion')
        metrics['restored_archive_complete_seconds'] = monotonic() - restart_started
        before['Current'] -= 1
        self.assertEqual(before, status_counts(probe))
        self.assertEqual([[parent, files[1].name, 'Offline edit 2']], probe.rows(query('AN-T-2')))
        self.assertEqual([[parent, moved.name, 'Current 3']], probe.rows(query('AN-T-3')))
        self.assertEqual([], probe.rows(query('AN-T-4')))
        self.assertEqual(restarted, probe.rows(query('AN-T-1')))
        self.assertEqual(disk, probe.disk())
        probe.until(lambda: public_ready(probe), 'restart public health')
        asyncio.run(self._mcp_query(probe.url))

    async def _mcp_query(self, url):
        async with image_mcp_transport(url + '/anechoic/mcp') as streams, ClientSession(*streams) as client:
            await client.initialize()
            result = await client.call_tool('query_run', {'sql': 'SELECT 1 AS ready', 'result_delivery': 'inline'})
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual([[1]], result.structured_content['rows'])
