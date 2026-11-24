from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
    capture, code_access_occurrences, resolve_realization,
)


class WebImportTests(TestCase):
    def test_web_sites_resolve_and_keep_positions_and_types(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            files = {
                'package.json': '{"dependencies":{"example":"1"}}',
                'pkg/entry.ts': "import type { X } from './lib/shared';\nimport './view.css';\nexport { X } from './lib/shared';\nimport('missing-alias');\nrequire(variable);\nimport 'example/sub';\n",
                'pkg/lib/shared.ts': 'export type X = string;',
                'pkg/view.css': '',
                'pkg/component.svelte': '<script lang="ts">import type { X } from "./lib/shared";</script><p>Hello</p>',
                'pkg/bad.js': 'import {',
            }
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            sources = capture(root, None)
            self.assertEqual(sources['pkg/entry.ts'].status, 'parsed')
            self.assertEqual(sources['pkg/bad.js'].status, 'parse_error')
            _, occurrences, edges, _, _ = resolve_realization(root, sources)
            rows = {(r[1], r[3]): r for r in occurrences}
            row = next(r for r in occurrences if r[1] == 'module:pkg/entry.ts' and r[3] == './lib/shared' and r[4] == 1)
            self.assertEqual((row[2], row[4], row[5], row[6], row[7]), ('module:pkg/lib/shared.ts', 1, 0, 'internal', True))
            self.assertEqual(rows['module:pkg/entry.ts', './view.css'][6], 'asset')
            self.assertEqual(rows['module:pkg/entry.ts', 'missing-alias'][6], 'unresolved')
            self.assertEqual(rows['module:pkg/entry.ts', '<dynamic>'][6], 'unresolved')
            self.assertEqual(rows['module:pkg/entry.ts', 'example/sub'][6], 'external')
            self.assertFalse(any(edge[2] == rows['module:pkg/entry.ts', './view.css'][0] for edge in edges))
            self.assertEqual(rows['module:pkg/component.svelte', './lib/shared'][5], 18)
            _, facts = code_access_occurrences(root, sources)
            self.assertTrue(any(f.source_path == 'pkg/entry.ts' and f.target_path == 'pkg/lib/shared.ts' for f in facts))

    def test_asset_targets_are_available_to_code_access(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            tests = root / 'app__tests' / 'fixtures'
            tests.mkdir(parents=True)
            (tests / 'style.css').write_text('')
            (tests / 'data.json').write_text('{}')
            imports = "import './app__tests/fixtures/style.css';\nimport './app__tests/fixtures/data.json';\n"
            (root / 'main.ts').write_text(imports)
            sources = capture(root, None)
            _, facts = code_access_occurrences(root, sources)
            _, rows, edges, _, _ = resolve_realization(root, sources)
        self.assertEqual([(fact.target_path, fact.target_kind, fact.status) for fact in facts], [
            ('app__tests/fixtures/' + name, 'asset', 'asset') for name in ('style.css', 'data.json')
        ])
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row[2] is None and row[6] == 'asset' for row in rows))
        self.assertEqual(edges, [])

    def test_missing_parser_is_explicitly_unsupported(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'entry.ts').write_text("import './other';")
            with patch('IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.web_imports.shutil.which', return_value=None):
                self.assertEqual(capture(root, None)['entry.ts'].status, 'unsupported')

    def test_vite_load_uses_only_known_frontend_root(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / 'package.json').write_text('{}')
            (root / 'src').mkdir()
            (root / 'src' / 'lib__shared.ts').write_text('export {};')
            (root / 'test.ts').write_text("server.ssrLoadModule('/src/lib__shared.ts');")
            sources = capture(root, None)
            site = sources['test.ts'].imports[0]
            self.assertEqual((site.module, site.level), ('/src/lib__shared.ts', 1))
            self.assertEqual(resolve_realization(root, sources)[1][0][6], 'unresolved')
            with patch('IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.web_imports._FRONTEND', root):
                row = resolve_realization(root, sources)[1][0]
            self.assertEqual((row[2], row[6]), ('module:src/lib__shared.ts', 'internal'))

    def test_create_require_literal_anchor_and_unknown_anchor(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / 'frontend').mkdir()
            (root / 'frontend' / 'package.json').write_text('{"devDependencies":{"example":"1"}}')
            (root / 'caller').mkdir()
            prefix = "import { createRequire } from 'node:module';\n"
            (root / 'caller' / 'known.mjs').write_text(prefix + "const require = createRequire(new URL('../frontend/package.json', import.meta.url));\nrequire('example');\n")
            (root / 'caller' / 'unknown.mjs').write_text(prefix + "const require = createRequire(computed);\nrequire('example');\n")
            sources = capture(root, None)
            _, rows, _, _, _ = resolve_realization(root, sources)
            found = {(row[1], row[3]): row[6] for row in rows}
            self.assertEqual(found['module:caller/known.mjs', 'example'], 'external')
            self.assertEqual(found['module:caller/unknown.mjs', 'example'], 'unresolved')
            _, facts = code_access_occurrences(root, sources)
            self.assertTrue(any(f.source_path == 'caller/known.mjs' and f.written == 'example' and f.unit is None for f in facts))
