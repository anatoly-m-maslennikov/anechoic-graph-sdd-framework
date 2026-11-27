import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native, canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged, create_draft, promote_draft


DRAFT_4856 = '''---
atom_family: SPEC
atom_id: AN-S-4856
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: draft
  version: 1
  updated_at: '2026-11-24T19:28:03+00:00'
---

## Summary

Declare Artifact Kind classification

## Claim scope

MODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification, Property

class Property4856(Property):
    name = 'Artifact Kind'
    bearer = Classification
    classification = True
    allowed_values = ('Artifact', 'Ephemeral')
```
'''


class FirstSpecRevisionCases:
    def test_first_unpinned_spec_publishes_its_version_and_cleans_up(self):
        for atom_id, lens, version in [('AN-S-8', 'SWD', 1), ('AN-S-9', 'SPEC', 3)]:
            suffix = lens + '--example.md'
            ref = f'{atom_id}@{version}-draft'
            draft = self.spec(f'UNIT_C9/01_draft/{ref}-{suffix}', atom_id, lens)
            header, body = draft.read_text().split('---\n', 2)[1:]
            data = yaml.safe_load(header)
            data['state'].update(status='draft', version=version)
            data['context']['tier'] = 3
            draft.write_text('---\n' + yaml.safe_dump(canonical_native_header(data), sort_keys=False) + '---\n' + body)
            params = {'target': {'ref_id': ref, 'version': version}, 'targetStatus': 'ready'}
            result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
            self.assertEqual('completed', result['outcome'], result)
            current = self.control / 'UNIT_C9' / '02_ready' / f'{atom_id}-{suffix}'
            self.assertEqual((current, version), (self.root / result['artifact']['path'], result['artifact']['version']))
            self.assertFalse(draft.exists())
            self.assertEqual(['create', 'remove'], [e['operation'] for e in result['effects'] if e.get('evidence') != 'directory'])
            self.assertFalse(capture_native(self.selection).errors)


    def test_first_typed_spec_accepts_valid_and_rejects_invalid_scope(self):
        source = DRAFT_4856
        name = 'AN-S-4856@1-draft-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md'
        path = self.control / 'UNIT_C9/01_draft' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        params = {'target': {'ref_id': 'AN-S-4856@1-draft', 'version': 1}, 'targetStatus': 'ready'}
        invalid = source.replace('MODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind', 'invalid scope')
        path.write_text(invalid)
        with self.assertRaises(InputError):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual(invalid, path.read_text())
        self.assertFalse((path.parent.parent / '02_ready').exists())
        path.write_text(source)
        result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'], result)
        ready = self.root / result['artifact']['path']
        self.assertEqual('AN-S-4856-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md', ready.name)
        self.assertEqual('ready', yaml.safe_load(ready.read_text().split('---', 2)[1])['state']['status'])
        self.assertFalse(path.exists())

    def test_first_spec_cleanup_failure_can_retry_without_rewriting(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import effects_module as effects
        draft = self.spec('UNIT_C9/01_draft/AN-S-8@1-draft-DES--example.md', 'AN-S-8')
        draft.write_text(draft.read_text().replace('status: active', 'status: draft'))
        params = {'target': {'ref_id': 'AN-S-8@1-draft', 'version': 1}, 'targetStatus': 'ready'}
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('failed', result['outcome'])
        self.assertNotIn('artifact', result)
        self.assertTrue(draft.exists())
        result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(['remove'], [e['operation'] for e in result['effects']])
        self.assertFalse(draft.exists())


    def test_first_spec_preserves_other_drafts(self):
        old = self.spec('UNIT_C9/01_draft/AN-S-8@1-draft-DES--example.md', 'AN-S-8')
        old.write_text(old.read_text().replace('status: active', 'status: draft'))
        draft = self.spec('UNIT_C9/01_draft/AN-S-8@2-draft-DES--example.md', 'AN-S-8')
        draft.write_text(draft.read_text().replace('status: active', 'status: draft').replace('version: 1', 'version: 2'))
        original = old.read_bytes()
        result = promote_draft(self.selection,
            {'target': {'ref_id': 'AN-S-8@2-draft', 'version': 2}, 'targetStatus': 'ready'},
            current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(2, result['artifact']['version'])
        self.assertEqual(original, old.read_bytes())
        self.assertFalse(draft.exists())


    def test_first_spec_rejects_unsafe_or_stale_inputs(self):
        for case in ('owner', 'lens', 'template', 'manifest_name', 'filename', 'history', 'stale', 'status'):
            with self.subTest(case=case):
                name = ('SPEC-PROJECT_MANIFEST--example.md' if case == 'manifest_name' else
                        'SWD--example.md' if case == 'filename' else 'DES--example.md')
                draft = self.spec(f'UNIT_C9/01_draft/AN-S-8@1-draft-{name}', 'AN-S-8',
                                  'invalid/lens!' if case == 'lens' else 'DES', 'C8' if case == 'owner' else 'C9')
                header, body = draft.read_text().split('---\n', 2)[1:]
                data = yaml.safe_load(header)
                data['state']['status'] = 'draft'
                if case == 'filename':
                    data['context']['tier'] = 3
                if case == 'template':
                    data['context']['template'] = 'component_manifest'
                draft.write_text('---\n' + yaml.safe_dump(canonical_native_header(data) if case == 'filename' else data) + '---\n' + body)
                history = None
                if case == 'history':
                    history = self.spec('UNIT_C9/09_archived/AN-S-8@2-DES--example.md', 'AN-S-8')
                    history.write_text(history.read_text().replace('status: active', 'status: archived').replace('version: 1', 'version: 2'))
                rows = capture_native(self.selection).atoms
                if case == 'stale':
                    draft.write_bytes(draft.read_bytes() + b'changed')
                before = {p.relative_to(self.control): p.read_bytes() for p in self.control.rglob('*.md')}
                params = {'target': {'ref_id': 'AN-S-8@1-draft', 'version': 1},
                          'targetStatus': 'done' if case == 'status' else 'ready'}
                with self.assertRaises((InputError, SourceChanged)):
                    promote_draft(self.selection, params, current_rows=rows)
                self.assertEqual(before, {p.relative_to(self.control): p.read_bytes() for p in self.control.rglob('*.md')})
                draft.unlink()
                if history:
                    history.unlink()


    def test_template_recode_preserves_old_draft_and_archive_name(self):
        current = self.spec('UNIT_C9/_SPEC/AN-S-44-SPEC--example.md', 'AN-S-44', 'SPEC')
        _, text, body = current.read_text().split('---', 2)
        metadata = yaml.safe_load(text)
        metadata['context']['tier'] = 2
        body = body.replace('# Summary', '## Summary')
        body += '\n## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_relation\ndeclare_relation(relation_name="LINK", source_endpoint={}, target_endpoint={})\n```\n'
        current.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata), sort_keys=False) + '---' + body)
        def rows():
            return capture_native(self.selection).atoms
        params = {'sourceCurrent': {'ref_id': 'AN-S-44', 'version': 1}}
        first = create_draft(self.selection, params, current_rows=rows())['savedDraft']
        old_draft = self.root / first['path']
        old_bytes = old_draft.read_bytes()
        second = create_draft(self.selection, params, current_rows=rows())['savedDraft']
        draft = self.root / second['path']
        _, text, _ = draft.read_text().split('---', 2)
        metadata = yaml.safe_load(text)
        metadata['context']['template'] = 'manifest_relation'
        typed_body = ('\n## Summary\n\nExample\n\n## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Relation//LINK\n\n'
                      '## Formal Manifest\n\n```python anechoic-edsl\nfrom anechoic.model import Relation\n'
                      'class Link(Relation):\n    name = "LINK"\n    source_endpoint = {"level": "model_entities"}\n    target_endpoint = {"level": "model_entities"}\n```\n')
        draft.rename(draft.with_name('AN-S-44@3-draft-SPEC-MANIFEST_RELATION--example.md'))
        draft = draft.with_name('AN-S-44@3-draft-SPEC-MANIFEST_RELATION--example.md')
        draft.write_text('---\n' + yaml.safe_dump(metadata, sort_keys=False) + '---' + typed_body)
        result = promote_draft(self.selection, {'target': {'ref_id': 'AN-S-44@3-draft', 'version': 3},
                                               'targetStatus': 'ready'}, current_rows=rows())
        self.assertEqual('completed', result['outcome'], result)
        self.assertTrue((self.control / 'UNIT_C9/02_ready/AN-S-44-SPEC-MANIFEST_RELATION--example.md').exists())
        self.assertTrue((self.control / 'UNIT_C9/09_archived/AN-S-44@1-SPEC--example.md').exists())
        self.assertEqual(old_bytes, old_draft.read_bytes())
        self.assertTrue(any(row.get('_exact_ref') == 'AN-S-44@3' and row.get('status') == 'ready' for row in rows()))

    def test_constraints_callback_and_non_formal_predecessor(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards import _validate_c9_typed_manifest, _has_formal_declaration
        header = {'atom_family': 'SPEC', 'atom_id': 'AN-S-3147', 'container': {'component': 'C9'}, 'tier': 2,
                  'context': {'lens': 'SPEC', 'template': 'manifest_node'},
                  'state': {'status': 'draft', 'version': 2, 'updated_at': '2026-11-24T00:00:00Z'}}
        body = ('## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Node//Atom.Constraints\n\n## Formal Manifest\n\n'
                '```python anechoic-edsl\nfrom anechoic.model import Atom, NodeConstraints\n'
                'def check_atom(atom: Atom) -> bool:\n    return True\n'
                'class Constraints(NodeConstraints):\n    bearer = Atom\n    instance_check = check_atom\n```\n')
        _validate_c9_typed_manifest(header, body)
        with self.assertRaises(InputError):
            _validate_c9_typed_manifest(header, body.replace('class Constraints', 'print(1)\nclass Constraints'))
        self.assertFalse(_has_formal_declaration('## Claim\n\nProse.\n'))

    def test_continuant_typed_manifest_requires_concern_and_no_claim_scope(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards import is_c9_typed_manifest, _validate_c9_typed_manifest
        header = {'atom_family': 'SPEC', 'atom_id': 'AN-S-100', 'container': {'component': 'C9'}, 'tier': 2,
                  'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-11-24T00:00:00Z'},
                  'concern': {'subject': 'Atom', 'path': 'Model/Graph/Node', 'relation': 'is_narrower_than'},
                  'context': {'lens': 'DOM/CONT', 'template': 'manifest_node'}}
        body = ('## Formal Manifest\n\n```python anechoic-edsl\n'
                'from anechoic.model import Node\nclass Atom(Node):\n    pass\n```\n')
        self.assertTrue(is_c9_typed_manifest(header))
        _validate_c9_typed_manifest(header, body)
        for concern in (None, {}, {'subject': 'Atom'}, {**header['concern'], 'relation': 'unknown'}):
            with self.subTest(concern=concern), self.assertRaises(InputError):
                _validate_c9_typed_manifest({**header, 'concern': concern}, body)
        with self.assertRaises(InputError):
            _validate_c9_typed_manifest(header, '## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Node//Atom\n\n' + body)

    def test_continuant_revision_accepts_legacy_typed_header_migration(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_revision import _check_revision_headers
        previous = {'atom_family': 'SPEC', 'container': {'component': 'C9'}, 'tier': 2,
                    'context': {'lens': 'SPEC', 'template': 'manifest_node'}}
        draft = {**previous, 'concern': {'subject': 'Atom', 'path': 'Model/Graph/Node', 'relation': 'is_narrower_than'},
                 'context': {'lens': 'DOM/CONT', 'template': 'manifest_node'}}
        body = '## Summary\n\nExample\n'
        _check_revision_headers(draft, previous, body, body, True)
        with self.assertRaises(InputError):
            _check_revision_headers({**draft, 'tier': 3}, previous, body, body, True)

    def test_first_continuant_manifest_promotes_to_ready(self):
        header_text, body = DRAFT_4856.split('---\n', 2)[1:]
        header = yaml.safe_load(header_text)
        header['context']['lens'] = 'DOM/CONT'
        header['concern'] = {'subject': 'Artifact Kind', 'path': 'Model/Graph/Classification', 'relation': 'classifies'}
        body = body.replace('## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind\n\n', '')
        path = self.control / 'UNIT_C9/01_draft/AN-S-4856@1-draft-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) + '---\n' + body)
        result = promote_draft(self.selection,
            {'target': {'ref_id': 'AN-S-4856@1-draft', 'version': 1}, 'targetStatus': 'ready'},
            current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'], result)
        self.assertEqual('AN-S-4856-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md',
                         (self.root / result['artifact']['path']).name)

    def test_continuant_revision_promotes_legacy_typed_manifest(self):
        current = self.control / 'UNIT_C9/_SPEC/AN-S-4856-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md'
        current.parent.mkdir(parents=True, exist_ok=True)
        current.write_text(DRAFT_4856.replace('status: draft', 'status: active'))
        def rows():
            return capture_native(self.selection).atoms
        saved = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-S-4856', 'version': 1}},
                             current_rows=rows())['savedDraft']
        draft = self.root / saved['path']
        _, text, body = draft.read_text().split('---\n', 2)
        header = yaml.safe_load(text)
        header['context']['lens'] = 'DOM/CONT'
        header['concern'] = {'subject': 'Artifact Kind', 'path': 'Model/Graph/Classification', 'relation': 'classifies'}
        body = body.replace('## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind\n\n', '')
        draft.rename(draft.with_name('AN-S-4856@2-draft-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md'))
        draft = draft.with_name('AN-S-4856@2-draft-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md')
        draft.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) + '---\n' + body)
        result = promote_draft(self.selection, {'target': {'ref_id': 'AN-S-4856@2-draft', 'version': 2},
                                               'targetStatus': 'ready'}, current_rows=rows())
        self.assertEqual('completed', result['outcome'], result)
        self.assertTrue((self.control / 'UNIT_C9/09_archived/AN-S-4856@1-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md').exists())
        self.assertTrue((self.root / result['artifact']['path']).exists())
