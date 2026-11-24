import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import TechnicalDiagnosticLogger
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE import timing


class LogLevelTests(unittest.TestCase):
    def test_severity_thresholds_and_default(self):
        levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        for threshold in levels:
            stream = io.StringIO()
            logger = TechnicalDiagnosticLogger(None, None, 'test', stream, 'host')
            with self.subTest(threshold=threshold), patch.dict(os.environ, {'ANECHOIC_LOG_LEVEL': threshold}):
                for severity in levels:
                    self.assertIsNone(logger.emit(severity=severity, code='x', relative_path='', reason=''))
                self.assertEqual(list(levels[levels.index(threshold):]),
                                 [json.loads(line)['severity'] for line in stream.getvalue().splitlines()])
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, 'test', stream, 'host')
        with patch.dict(os.environ):
            os.environ.pop('ANECHOIC_LOG_LEVEL', None)
            with patch.object(TechnicalDiagnosticLogger, '_record', side_effect=AssertionError('serialized')):
                self.assertIsNone(logger.emit(severity='DEBUG', code='x', relative_path='', reason=''))
        self.assertEqual('', stream.getvalue())

    def test_invalid_setting_and_sink_failure_are_secondary(self):
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, None, 'test', stream, 'host')
        with patch.dict(os.environ, {'ANECHOIC_LOG_LEVEL': 'info'}):
            self.assertEqual('invalid ANECHOIC_LOG_LEVEL', logger.emit(code='x', relative_path='', reason=''))
        self.assertEqual('', stream.getvalue())
        with patch.dict(os.environ, {'ANECHOIC_LOG_LEVEL': 'INFO'}):
            stream.close()
            self.assertIsNotNone(logger.emit(code='x', relative_path='', reason=''))

    def test_timing_uses_debug_and_stderr_when_context_exists(self):
        selection = SimpleNamespace(settings={}, root=Path('/project'))
        with patch.object(timing, 'make_technical_logger', return_value=(None, None)) as factory:
            timing._logger(selection)
        self.assertIs(factory.call_args.kwargs['stream'], sys.stderr)
        stream = io.StringIO()
        logger = TechnicalDiagnosticLogger(None, Path('/project'), 'test', stream, 'host')
        token = timing._context.set(('atom_lifecycle_archive', logger))
        try:
            with patch.dict(os.environ, {'ANECHOIC_LOG_LEVEL': 'DEBUG'}):
                with timing.span('test'):
                    pass
        finally:
            timing._context.reset(token)
        self.assertEqual(['started', 'done'], [json.loads(line)['outcome'] for line in stream.getvalue().splitlines()])
        self.assertTrue(all(json.loads(line)['severity'] == 'DEBUG' for line in stream.getvalue().splitlines()))


if __name__ == '__main__':
    unittest.main()
