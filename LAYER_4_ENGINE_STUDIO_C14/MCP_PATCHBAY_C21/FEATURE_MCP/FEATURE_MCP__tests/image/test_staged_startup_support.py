"""Check that the staged startup probe reports an impossible barrier."""

import unittest
from unittest.mock import Mock

from .staged_startup__support import PackagedProbe


class ArchiveBarrierTests(unittest.TestCase):
    def test_startup_completes_without_scheduling_archive(self):
        probe = Mock()
        probe.archive_marker.return_value = ''
        probe.jobs.return_value = {'latest': {'state': 'succeeded'}, 'archive': None}
        probe.health.return_value = {'archive_pending': True}
        self.assertEqual('', PackagedProbe.stopped(probe))
        probe.health.return_value['archive_pending'] = False
        with self.assertRaisesRegex(RuntimeError, 'without scheduling the expected archive Worker'):
            PackagedProbe.stopped(probe)
