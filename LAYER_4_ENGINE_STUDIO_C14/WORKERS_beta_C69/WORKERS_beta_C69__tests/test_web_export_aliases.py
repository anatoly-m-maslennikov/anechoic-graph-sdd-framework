import importlib.util
from pathlib import Path
import shutil
import unittest


WORKER = Path(__file__).resolve().parents[1]
FRONTEND = WORKER.parent / 'IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND'
spec = importlib.util.spec_from_file_location('web_export_aliases', WORKER / 'web_export_aliases.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(shutil.which('node') and (FRONTEND / 'node_modules/typescript').is_dir(),
                     'Framework web parser is unavailable')
class WebExportAliasTests(unittest.TestCase):
    def test_named_and_chained_aliases_and_shadowing(self):
        texts = {
            'owner.ts': 'export const state = {}; export const values = [];',
            'consumer.ts': "import { state as shared } from './owner';\nconst a = shared;\nconst b = a;\nshared.x = 1;\nb.y++;\nfunction f(shared: any) { shared.x = 2; }\nb[key] = 3;\n",
        }
        occurrences = [('x', 'module:consumer.ts', 'module:owner.ts', './owner', 1, 0, 'internal', False)]
        self.assertEqual(module.web_export_aliases(texts, occurrences), [
            ('consumer.ts', 4, 0, 'owner.ts', 'state'),
            ('consumer.ts', 5, 0, 'owner.ts', 'state'),
        ])

    def test_unresolved_and_type_only(self):
        texts = {'a.ts': "import { state as s } from 'missing';\nconst a = s;\na.x = 1;\nimport type { T } from 'types';\nT.x = 1;\n"}
        occurrences = [('x', 'module:a.ts', None, 'missing', 1, 0, 'external', False),
                       ('y', 'module:a.ts', None, 'types', 4, 0, 'external', True)]
        self.assertEqual(module.web_export_aliases(texts, occurrences), [('a.ts', 3, 0, None, 'state')])

    def test_ambiguous_and_unrecognizable_exports_stay_unresolved(self):
        texts = {'owner.ts': 'export let state = {};',
                 'a.ts': "import { state } from './owner';\nstate.x = 1;\n"}
        occurrence = ('x', 'module:a.ts', 'module:owner.ts', './owner', 1, 0, 'internal', False)
        self.assertEqual(module.web_export_aliases(texts, [occurrence]), [('a.ts', 2, 0, None, 'state')])
        ambiguous = ('y', 'module:a.ts', None, './owner', 1, 0, 'external', False)
        self.assertEqual(module.web_export_aliases(texts, [occurrence, ambiguous]), [('a.ts', 2, 0, None, 'state')])
