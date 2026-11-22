"""Generated native lifecycle paths; each case uses a fresh project."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures







class LifecycleRouteSupport:
    def project(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / '.git').mkdir()
        control = root / '.anechoic_test'
        control.mkdir()
        manifest = control / 'AN-S-1-PROJECT_MANIFEST--manifest.md'
        owner = control / '001_TICKETS/TASKS/AN-T-1-TASK--owner.md'
        owner.parent.mkdir(parents=True)
        for path, identity, template in ((manifest, 'AN-S-1', 'project_manifest'),
                                          (owner, 'AN-T-1', 'task')):
            header = {'identity': {'atom_id': identity},
                      'context': {'container': {'component': 'C00'}, 'template': template},
                      'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'}}
            path.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nOwner\n')
        return SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                               manifest_sha256=sha256(manifest.read_bytes()).hexdigest(), project_prefix='AN')

    def files(self, project):
        return {p.relative_to(project.root): p.read_bytes() for p in project.control_root.rglob('*') if p.is_file()}

    write = fixtures.NativeDraftTests.write
