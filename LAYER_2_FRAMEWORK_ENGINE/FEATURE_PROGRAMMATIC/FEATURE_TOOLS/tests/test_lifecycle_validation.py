from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from ATOM_LIFECYCLE.carrier import render_carrier  # noqa: E402
from ATOM_LIFECYCLE.common import InputError  # noqa: E402
from ATOM_LIFECYCLE.status_model import StatusModel  # noqa: E402
from ATOM_LIFECYCLE.validation import validate_candidate  # noqa: E402


class CandidateValidationTests(unittest.TestCase):
    def test_direct_update_checks_generated_model_before_saving(self):
        from dataclasses import replace
        import tempfile
        from ATOM_LIFECYCLE.backend import execute
        from ATOM_LIFECYCLE.candidate_schema import compile_candidate_schema, load_candidate_schema
        from lifecycle_placement_test_support import fixture_rules
        from project_selection import resolve_project
        from scope_declaration_test_support import write_scope_unit_declarations
        from test_lifecycle_candidate_schema import CORE

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            asset = root / 'schema.json'
            asset.write_bytes(compile_candidate_schema(CORE))
            schema = replace(load_candidate_schema(asset), placement=fixture_rules())
            self.assertIsNotNone(schema.work_report_target)
            control = root / '.caprmedio_test'
            control.mkdir()
            (control / 'caprmedio_project_settings.toml').write_text(
                '[project]\nname="TEST"\n[artifacts.identity]\nproject_prefix="CA"\n'
                '[paths]\ncontrol_root=".caprmedio_test"\n')
            write_scope_unit_declarations(root, control_root=control, rows=[])
            selection = resolve_project(root)
            target = control / '03_plan/done/CA-P-1-TASK--same-work.md'
            target.parent.mkdir(parents=True)
            fields = {'atom_id': 'CA-P-1', 'ref_id': 'CA-P-1', 'role': 'Plan', 'form': 'Plan',
                      'status': 'Done', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                      'container.scope_unit': 'TEST', 'tier': 0,
                      'topics': {'main_subject': 'CAPRMEDIO_MODEL <+ Atom'}}
            target.write_bytes(render_carrier(None, fields, body='## Summary\n\nSame work\n'))
            report = fields | {'atom_id': 'CA-P-2', 'ref_id': 'CA-P-2', 'form': 'Work Report',
                               'relations': {'IS_WORK_REPORT_FOR': ['CA-P-1']}}
            path = target.with_name('CA-P-2-WORK_REPORT--same-work.md')
            body = '## Summary\n\nSame work\n\n## Details\n\n'
            path.write_bytes(render_carrier(None, report, body=body + 'Before\n'))
            model = StatusModel(((None, None, 'Done'),), candidate_schema=schema)
            params = {'target': {'ref_id': 'CA-P-2', 'version': 1}}
            updated = execute(selection, model, 'atom_lifecycle_direct_update',
                              params | {'changes': {'body': body + 'After\n',
                                                    'relations': {'is_work_report_for': ['CA-P-1']}}})
            self.assertEqual(updated['outcome'], 'completed', updated)
            path = root / updated['artifact']['path']
            saved = path.read_bytes()
            self.assertIn(b'After\n', saved)
            entity_rules = schema.header_relation_rules['entity_rules']
            atom_rule = {'SPECIALIZES': {'targets_per_source': 0}}
            links = {'is_work_report_for': ['CA-P-1'], 'SPECIALIZES': ['CA-P-1']}
            with patch.dict(entity_rules['Atom'], atom_rule):
                refused = execute(selection, model, 'atom_lifecycle_direct_update',
                                  params | {'changes': {'relations': links}})
                self.assertEqual(refused['outcome'], 'needs_input', refused)
                self.assertIn('target count', refused['requested_input']['relations']['error'])
                self.assertEqual(saved, path.read_bytes())
                with patch.dict(entity_rules['WorkReport'], {'SPECIALIZES': {'targets_per_source': 1}}):
                    outcome = execute(selection, model, 'atom_lifecycle_direct_update',
                                      params | {'changes': {'relations': links}})
                    self.assertEqual(outcome['outcome'], 'completed', outcome)
                    path = root / outcome['artifact']['path']
                    path.write_bytes(saved)
            refused = execute(selection, model, 'atom_lifecycle_direct_update',
                              params | {'changes': {'ai_agent_confidence_threshold': 101}})
            self.assertEqual(refused['outcome'], 'needs_input', refused)
            self.assertIn('at most 100', refused['requested_input']['ai_agent_confidence_threshold']['error'])
            self.assertEqual(saved, path.read_bytes())

            bad_context = saved.replace(b'context:\n', b'context:\n  extra: true\n', 1)
            self.assertNotEqual(saved, bad_context)
            path.write_bytes(bad_context)
            refused = execute(selection, model, 'atom_lifecycle_direct_update',
                              params | {'changes': {'body': body + 'Rejected\n'}})
            self.assertEqual(refused['outcome'], 'needs_input', refused)
            self.assertIn('requires 5..7 children', refused['requested_input']['context']['error'])
            self.assertEqual(bad_context, path.read_bytes())
            path.write_bytes(saved)

            invalid_destination = {'file': {'name': path.name, 'path': 123}}
            with patch('ATOM_LIFECYCLE.state_actions._destination_field', return_value=invalid_destination):
                refused = execute(selection, model, 'atom_lifecycle_direct_update',
                                  params | {'changes': {'body': body + 'Rejected\n'}})
            self.assertEqual(refused['outcome'], 'needs_input', refused)
            self.assertIn('file.path', refused['requested_input']['destination']['error'])
            self.assertEqual(saved, path.read_bytes())

            refused = execute(selection, model, 'atom_lifecycle_direct_update',
                              params | {'changes': {'topics': {'main_subject': ['one', 'two']}}})
            self.assertEqual(refused['outcome'], 'needs_input', refused)
            self.assertIn('main_subject', refused['requested_input'])
            self.assertEqual(saved, path.read_bytes())
            for subject in ('CAPRMEDIO_MODEL <+ Missing', 'CAPRMEDIO_STRUCTURE <+ Scope Unit//Missing'):
                refused = execute(selection, model, 'atom_lifecycle_direct_update',
                                  params | {'changes': {'topics': {'main_subject': subject}}})
                self.assertEqual(refused['outcome'], 'needs_input', refused)
                self.assertIn('main_subject', refused['requested_input'])
                self.assertEqual(saved, path.read_bytes())

            for relations, error in (
                ({}, 'target count'),
                ({'IS_WORK_REPORT_FOR': []}, 'target count'),
                ({'IS_WORK_REPORT_FOR': 'CA-P-1'}, 'list of Project base Atom IDs'),
                ({'IS_WORK_REPORT_FOR': ['CA-P-1@1']}, 'list of Project base Atom IDs'),
                ({'UNDECLARED_TEST_RELATION': ['CA-P-1']}, 'declared direct Relation name'),
                ({'BLOCKS': ['CA-P-1']}, 'declared direct Relation name'),
                ({'IS_CONTAINED_BY': ['CA-P-1']}, 'supplied by Container or Main Subject'),
            ):
                with self.subTest(relations=relations):
                    refused = execute(selection, model, 'atom_lifecycle_direct_update',
                                      params | {'changes': {'relations': relations}})
                    self.assertEqual(refused['outcome'], 'needs_input', refused)
                    self.assertIn(error, refused['requested_input']['relations']['error'])
                    self.assertEqual(saved, path.read_bytes())

            target.with_name('CA-P-4-WORK_REPORT--same-work.md').write_bytes(saved.replace(b'CA-P-2', b'CA-P-4'))
            for refs, error in ((['CA-P-1', 'CA-P-3'], 'target count'),
                                (['CA-P-4'], 'endpoint levels or kinds are not admitted')):
                with self.subTest(refs=refs):
                    refused = execute(selection, model, 'atom_lifecycle_direct_update',
                                      params | {'changes': {'relations': {'IS_WORK_REPORT_FOR': refs}}})
                    self.assertEqual(refused['outcome'], 'needs_input', refused)
                    self.assertIn(error, refused['requested_input']['relations']['error'])
                    self.assertEqual(saved, path.read_bytes())

            undeclared = saved.replace(b'identity:\n', b'identity:\n  extra: true\n', 1)
            self.assertNotEqual(saved, undeclared)
            path.write_bytes(undeclared)
            refused = execute(selection, model, 'atom_lifecycle_direct_update',
                              params | {'changes': {'body': body + 'Rejected\n'}})
            self.assertEqual(refused['outcome'], 'needs_input', refused)
            self.assertIn('Undeclared properties: extra', refused['requested_input']['identity']['error'])
            self.assertEqual(undeclared, path.read_bytes())

            path.write_bytes(saved)
            draft = target.parent.parent / 'draft/CA-P-2@1-draft-WORK_REPORT--same-work.md'
            draft.parent.mkdir()
            draft.write_bytes(render_carrier(saved, {'status': 'draft', 'ref_id': 'CA-P-2@1-draft'}))
            draft_bytes = draft.read_bytes()
            updated = execute(selection, model, 'atom_lifecycle_direct_update',
                              params | {'changes': {'body': body + 'Updated without checking Draft history\n'}})
            self.assertEqual(updated['outcome'], 'completed', updated)
            self.assertEqual(draft_bytes, draft.read_bytes())
            self.assertIn(b'Updated without checking Draft history', path.read_bytes())

    def test_batch_stops_after_first_generated_model_failure(self):
        from contextlib import redirect_stderr
        from dataclasses import replace
        from io import StringIO
        from tempfile import TemporaryDirectory
        from ATOM_LIFECYCLE.backend import execute
        from ATOM_LIFECYCLE.candidate_schema import compile_candidate_schema, load_candidate_schema
        from lifecycle_placement_test_support import fixture_rules
        from project_selection import resolve_project
        from scope_declaration_test_support import write_scope_unit_declarations
        from test_lifecycle_candidate_schema import CORE

        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control = root / '.caprmedio_test'
            folder = control / '04_requirement'
            folder.mkdir(parents=True)
            (control / 'caprmedio_project_settings.toml').write_text(
                '[project]\nname="TEST"\n[artifacts.identity]\nproject_prefix="CA"\n'
                '[paths]\ncontrol_root=".caprmedio_test"\n')
            write_scope_unit_declarations(root, control_root=control, rows=[])
            asset = root / 'schema.json'
            asset.write_bytes(compile_candidate_schema(CORE))
            schema = replace(load_candidate_schema(asset), placement=fixture_rules())
            model = StatusModel(((None, None, 'Active'), (None, None, 'Archived')), candidate_schema=schema)
            entries, before = self._batch_fixture_carriers(folder)
            stderr = StringIO()
            with redirect_stderr(stderr):
                result = execute(resolve_project(root), model, 'atom_lifecycle_archive', {'targets': entries})
            self.assertEqual('failed', result['outcome'], result)
            self.assertEqual(entries[2:], result['remaining_targets'])
            self.assertIn('Undeclared properties: extra', stderr.getvalue())
            self.assertFalse(next(iter(before)).exists())
            self.assertEqual(1, len(list(folder.glob('archived/CA-R-201@1-*.md'))))
            for path, raw in list(before.items())[1:]:
                self.assertEqual(raw, path.read_bytes())

    def _batch_fixture_carriers(self, folder):
        entries, before = [], {}
        for number in (201, 202, 203):
            ref = f'CA-R-{number}'
            path = folder / f'{ref}-REQUIREMENT--example.md'
            fields = {'atom_id': ref, 'ref_id': ref, 'role': 'Requirement', 'form': 'Requirement',
                      'status': 'Active', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                      'container.scope_unit': 'TEST', 'tier': 0,
                      'topics': {'main_subject': 'CAPRMEDIO_MODEL <+ Atom'},
                      'destination': {'file': {'name': path.name, 'path': path.parent.name}}}
            raw = render_carrier(None, fields, body='## Summary\n\nExample\n\n## Claim\n\n'
                                                   '### Prose Claim\n\nExample claim.\n')
            if number == 202:
                raw = raw.replace(b'context:\n', b'context:\n  extra: true\n', 1)
            path.write_bytes(raw)
            entries.append({'target': {'ref_id': ref, 'version': 1}})
            before[path] = raw
        return entries, before

    def test_generated_context_accepts_carrier_aliases_and_rejects_unknown_priority(self):
        from ATOM_LIFECYCLE.atom_header_validation import validate_context_fields
        from carrier_aliases import carrier_read_view

        grouped = {'context': {'role': 'concern', 'form': 'problem', 'concern': {'priority': 'high'}}}
        legacy = {'role': 'Concern', 'form': 'Problem', 'priority': 'High'}
        for carrier in (grouped, legacy):
            validate_context_fields(carrier_read_view(carrier))
        split = {'main_subject': {'continuant': ['Atom']}, 'dependencies': {'occurrent': ['Runtime']}}
        validate_context_fields(carrier_read_view(legacy | {'topics': split, 'tier': 1}))
        with self.assertRaisesRegex(InputError, 'priority: value must be one of'):
            validate_context_fields(carrier_read_view(legacy | {'priority': 'urgent'}))
        with self.assertRaisesRegex(InputError, 'at least -1'):
            validate_context_fields(carrier_read_view(legacy | {'tier': -2}))

    def test_authored_work_report_requires_one_matching_current_plan(self):
        from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier

        selection = SimpleNamespace(settings={'artifacts': {'identity': {'project_prefix': 'CA'}}})
        model = StatusModel(((None, None, 'Active'), ('Plan', None, 'Done'), (None, None, 'Archived')))
        target_fields = {'atom_id': 'CA-P-1', 'ref_id': 'CA-P-1', 'role': 'Plan', 'form': 'Plan',
                         'status': 'Done', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                         'container.scope_unit': 'CA-SU-1'}
        target_raw = render_carrier(None, target_fields, body='## Summary\n\nSame work\n')
        target = SimpleNamespace(status='done', raw=target_raw, path=Path('plan.md'),
                                 metadata=parse_carrier(target_raw, Path('plan.md')).metadata)
        fields = target_fields | {'atom_id': 'CA-P-2', 'ref_id': 'CA-P-2', 'form': 'Work Report',
                                  'relations': {'IS_WORK_REPORT_FOR': ['CA-P-1']}}
        def check(values, body='## Summary\n\nSame work\n', **kwargs):
            validate_candidate(selection, model, render_carrier(None, values, body=body), Path('report.md'), **kwargs)

        with patch('ATOM_LIFECYCLE.validation.select_source', return_value=target) as select:
            check(fields)
            check(fields | {'relations': {'is_work_report_for': ['CA-P-1']}})
            self.assertEqual(select.call_args.args[1], 'CA-P-1')
            invalid_relations = ({}, {'IS_WORK_REPORT_FOR': []}, {'IS_WORK_REPORT_FOR': ['CA-P-1@1']},
                                 {'IS_WORK_REPORT_FOR': ['CA-P-2']}, {'IS_WORK_REPORT_FOR': ['CA-P-1', 'CA-P-3']},
                                 {'IS_WORK_REPORT_FOR': ['CA-P-1'], 'is_work_report_for': ['CA-P-3']})
            for relations in invalid_relations:
                with self.subTest(relations=relations), self.assertRaises(InputError):
                    check(fields | {'relations': relations})
            with self.assertRaisesRegex(InputError, 'same Summary'):
                check(fields, body='## Summary\n\nOther work\n')
            with self.assertRaisesRegex(InputError, 'same Container'):
                check(fields | {'container.scope_unit': 'CA-SU-2'})
            with self.assertRaisesRegex(InputError, 'Plan Role'):
                check(fields | {'atom_id': 'CA-M-2', 'ref_id': 'CA-M-2', 'role': 'Method', 'status': 'Active'})
            check(fields | {'relations': {}}, authored=False)
            check(fields | {'relations': {}, 'status': 'Archived'})
            for invalid in (SimpleNamespace(**{**target.__dict__, 'status': 'archived'}),
                            SimpleNamespace(**{**target.__dict__, 'metadata': {'role': 'Plan', 'form': 'Work Report'}})):
                select.return_value = invalid
                with self.assertRaises(InputError):
                    check(fields)

    def test_nonterminal_plan_is_rejected_under_any_terminal_ancestor(self):
        selection = SimpleNamespace(settings={'artifacts': {'identity': {'project_prefix': 'CA'}}})
        model = StatusModel(((None, None, 'Active'), ('Plan', None, 'Done')))
        fields = {'atom_id': 'CA-P-3', 'ref_id': 'CA-P-3', 'role': 'Plan', 'form': 'Plan',
                  'status': 'Active', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                  'container.atom': 'CA-P-2'}
        parents = {
            'CA-P-2': SimpleNamespace(status='active', metadata={'container': {'atom': 'CA-P-1'}}),
            'CA-P-1': SimpleNamespace(status='done', metadata={'container': {'scope_unit': 'CA-SU-1'}}),
        }
        with patch('ATOM_LIFECYCLE.validation.select_source', side_effect=lambda _, ref: parents[ref]):
            raw = render_carrier(None, fields, body='## Summary\n\nExample\n')
            with self.assertRaisesRegex(InputError, 'inside a Done or Canceled Plan'):
                validate_candidate(selection, model, raw, Path('candidate.md'))

    def test_required_identity_and_model_status(self):
        selection = SimpleNamespace(settings={'artifacts': {'identity': {'project_prefix': 'CA'}}})
        model = StatusModel(((None, None, 'Proposed'), ('Plan', None, 'Ready')))
        fields = {'atom_id': 'CA-P-1', 'ref_id': 'CA-P-1@1', 'role': 'Plan', 'form': 'Plan',
                  'status': 'Ready', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                  'container.scope_unit': 'CA-SU-1'}
        def check(values):
            validate_candidate(selection, model, render_carrier(None, values, body='## Summary\n\nExample\n'), Path('candidate.md'))
        check(fields)
        check(fields | {'status': 'ready'})
        with self.assertRaisesRegex(InputError, 'Role letter'):
            check(fields | {'atom_id': 'CA-R-1', 'ref_id': 'CA-R-1@1'})
        for key, value in (('status', 'Active'), ('version', True), ('ref_id', 'CA-P-2@1'),
                           ('container.scope_unit', ''), ('updated_at', '2026-01-01'), ('atom_id', 'CA-R-1')):
            with self.subTest(key=key), self.assertRaises(InputError):
                check(fields | {key: value})

    def test_global_form_validation_does_not_require_local_pair(self):
        from ATOM_LIFECYCLE.role_form_schema import RoleFormSchema

        selection = SimpleNamespace(
            settings={'artifacts': {'identity': {'project_prefix': 'CA'}}},
            structure={'scope_units': [
                {'parent': 'ROOT', 'scope_unit_name': 'SOURCE', 'scope_unit_id': 'CA-SU-1',
                 'admitted_role_forms': (('Method', 'Solution'), ('Evaluation', 'Direct Policy'))},
            ]},
        )
        roles = RoleFormSchema(frozenset({'Method', 'Evaluation'}),
                               frozenset({'Solution', 'Direct Policy', 'Approach Policy'}), frozenset(),
                               (('Direct Policy', frozenset({'Method'})),))
        noop = SimpleNamespace(validate=lambda _row: None)
        schema = SimpleNamespace(role_form=roles, validate_role_form=roles.validate, header=lambda _mode: noop,
                                 content=noop, content_constraints=noop,
                                 header_constraints=SimpleNamespace(validate=lambda *_args, **_kwargs: []))
        status = StatusModel(((None, None, 'Draft'),))
        model = SimpleNamespace(allowed=status.allowed, candidate_schema=schema)
        fields = {'atom_id': 'CA-M-1', 'ref_id': 'CA-M-1@1-draft', 'role': 'Method', 'form': 'Solution',
                  'status': 'Draft', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                  'container.scope_unit': 'CA-SU-1'}

        def check(values):
            validate_candidate(selection, model, render_carrier(None, values, body='## Summary\n\nExample\n'), Path('candidate.md'))

        check(fields)
        check(fields | {'container.scope_unit': 'SOURCE'})
        for form in ('Approach Policy', 'Direct Policy'):
            with self.subTest(form=form):
                check(fields | {'form': form})
        with self.assertRaisesRegex(InputError, 'not permitted'):
            check(fields | {'atom_id': 'CA-E-1', 'ref_id': 'CA-E-1@1-draft', 'role': 'Evaluation', 'form': 'Direct Policy'})


class DeclaredSchemaValidationTests(unittest.TestCase):
    def test_header_format_and_duplicate_declared_content(self):
        workbench = TOOLS.parents[0] / 'FEATURE_APPS/APP_WORKBENCH'
        sys.path.insert(0, str(workbench))
        from FEATURE_WORKBENCH_BACKEND.content_schema import (  # noqa: PLC0415
            ContentRule, DeclarationSource, _schema_from_rules,
        )
        from FEATURE_WORKBENCH_BACKEND.header_columns import HeaderColumn, HeaderSchema  # noqa: PLC0415
        from FEATURE_WORKBENCH_BACKEND.workbench_schema_asset import SchemaCompilation  # noqa: PLC0415
        from ATOM_LIFECYCLE.candidate_schema import CandidateSchema  # noqa: PLC0415
        from ATOM_LIFECYCLE.content_constraints import ContentConstraints  # noqa: PLC0415
        from ATOM_LIFECYCLE.header_constraints import HeaderConstraints  # noqa: PLC0415
        from ATOM_LIFECYCLE.role_form_schema import RoleFormSchema  # noqa: PLC0415

        header = HeaderSchema((HeaderColumn(('context', 'tier'), 'header.context.tier', 'BIGINT', True),))
        source = DeclarationSource(None, None, None)
        content = _schema_from_rules([ContentRule(('summary',), None, None, True, source)])
        role_form = RoleFormSchema(frozenset({'Plan'}), frozenset(), frozenset(), ())
        schema = CandidateSchema(SchemaCompilation(header, header, content), role_form,
                                 HeaderConstraints((), ()), ContentConstraints(()))
        selection = SimpleNamespace(settings={'artifacts': {'identity': {'project_prefix': 'CA'}}})
        status = StatusModel(((None, None, 'Proposed'),))
        model = SimpleNamespace(allowed=status.allowed, candidate_schema=schema)
        fields = {'atom_id': 'CA-P-1', 'ref_id': 'CA-P-1@1', 'role': 'Plan', 'form': 'Plan',
                  'status': 'Proposed', 'version': 1, 'updated_at': '2026-01-01T00:00:00+00:00',
                  'container.scope_unit': 'CA-SU-1', 'tier': 2}
        raw = render_carrier(None, fields, body='## Summary\n\nExample\n')
        validate_candidate(selection, model, raw, Path('candidate.md'))
        with self.assertRaises(InputError) as invalid_header:
            raw = render_carrier(None, fields | {'tier': 'bad'}, body='## Summary\n\nExample\n')
            validate_candidate(selection, model, raw, Path('candidate.md'))
        self.assertEqual(invalid_header.exception.field, 'tier')
        with self.assertRaises(InputError) as duplicate:
            raw = render_carrier(None, fields, body='## Summary\n\nOne\n\n## Summary\n\nTwo\n')
            validate_candidate(selection, model, raw, Path('candidate.md'))
        self.assertEqual(duplicate.exception.field, 'body')


if __name__ == '__main__':
    unittest.main()
