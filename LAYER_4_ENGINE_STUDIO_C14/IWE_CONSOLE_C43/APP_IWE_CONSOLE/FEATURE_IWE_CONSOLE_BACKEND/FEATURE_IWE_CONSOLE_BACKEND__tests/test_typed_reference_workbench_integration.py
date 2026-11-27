import unittest

class TypedReferenceWorkbenchIntegration(unittest.TestCase):
    def test_real_source_reader_and_standalone_workbench(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations
        from ..FEATURE_IWE_CONSOLE_BACKEND__shared import SourceReader, compile_project_schema
        base=Path('.anechoic_tmp/CA-P-3018/CA-P-3022');tmp=base/'wave16-typed-format';rootpath=Path.cwd()
        with TemporaryDirectory() as td:
         root=Path(td)/'project';root.mkdir();control=root/'.anechoic_anechoic';control.mkdir();(control/'anechoic_project_settings.toml').write_text('[project]\nname = "fixture"\n[artifacts.identity]\nproject_prefix = "CA"\n[paths]\ncontrol_root = ".anechoic_anechoic"\n')
         decl=write_scope_unit_declarations(root,({'scope_unit_name':'MAIN','scope_unit_type':'Ordered','scope_unit_label':'LAYER','local_order':1},),control_root=control)
         folder=Path(decl['MAIN']['authority_path'])/'04_requirement';folder.mkdir(parents=True,exist_ok=True)
         def write(ref,topic,body):
          path=folder/f'{ref}-DECLARATION.md';path.write_text(f'---\natom_id: "{ref}"\nrole: "Requirement"\nform: "Declaration"\nstatus: "Active"\nversion: 1\nupdated_at: "2026-11-04 00:00:00 +0000"\nsubjects:\n  governs: "{topic}"\nrelations: {{}}\n---\n'+body);return path
         binding_body='\n## Summary\n\nDeclare Named Selection\n\n## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import Continuant\n\nclass NamedSelection(Continuant):\n    pass\n\ndeclare_entity(\n    entity_class=NamedSelection,\n    entity_name="Named Selection",\n    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},\n)\n```\n\n## Semantics\n\nA Named Selection names criteria for choosing members. Selected members retain their identity.\n'
         dep_body='\n## Summary\n\nDeclare Projection.Source.Named Selection\n\n## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import NamedSelection\n\ndeclare_entity(\n    entity_name="Named Selection",\n    relation_name="IS_PROPERTY_OF",\n    base_path="Projection.Source",\n    property_occurrence_cardinality=1,\n    value_format=NamedSelection,\n    value_cardinality=1,\n    dependent_property_cardinality=0,\n)\n```\n\n'
         owner=write('CA-R-2587','ANECHOIC_MODEL <+ Named Selection',binding_body);dep=write('CA-R-2541','ANECHOIC_MODEL <+ Projection.Source.Named Selection',dep_body);unrelated=write('CA-R-990005','ANECHOIC_MODEL <+ Unrelated','## Summary\n\nUnrelated.\n')
         reader=SourceReader(root);rows,_=reader.capture();print('accepted',[(x['id'],x['source_path']) for x in rows]);print('errors',reader._diagnostics)
         assert {'CA-R-2587','CA-R-2541'}<={x['id'] for x in rows}
         print('standalone_schema_bytes',len(compile_project_schema(root)))
         from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_registry
         compile_registry(rows);print('registry','accepted typed Property')

         oldshape=reader._content_schema.schema.shape
         unrelated.write_text(unrelated.read_text().replace('Unrelated.','Unrelated change.'))
         reader.capture([{'operation':'update','old_path':None,'new_path':unrelated.relative_to(root).as_posix()}])
         assert reader._content_schema.schema.shape==oldshape
         print('unrelated_incremental','schema unchanged')
         self._assert_binding_changes(owner, reader, dep, root, write, binding_body)

    def _assert_binding_changes(self, owner, reader, dep, root, write, binding_body):
        from ..FEATURE_IWE_CONSOLE_BACKEND__shared import SourceReader, compile_project_schema
        original_owner=owner.read_text()
        from unittest.mock import patch
        owner.write_text(original_owner.replace('Named Selection','Different Selection'))
        with patch.object(reader, '_capture_full', wraps=reader._capture_full) as full:
         reader.capture([{'operation':'update','old_path':None,'new_path':owner.relative_to(root).as_posix()}])
         assert full.call_count >= 1
         assert reader._content_schema._bindings['NamedSelection']=={'Different Selection'}
         assert any('Different Selection//' in statement for statement, _source in reader._header_schema._contributions[dep.relative_to(root).as_posix()])
         print('target_move','recompiled complete capture')
        owner.write_text(original_owner)
        reader=SourceReader(root);reader.capture()
        owner.write_text(owner.read_text().replace('NamedSelection','RenamedSelection'))
        try:
         reader.capture([{'operation':'update','old_path':None,'new_path':owner.relative_to(root).as_posix()}])
         raise AssertionError('reader accepted missing class binding')
        except ValueError as e:
         assert str(e)=='missing or ambiguous Model class binding: NamedSelection'
         print('reader_incremental','rejected',type(e).__name__,str(e))
        try:compile_project_schema(root);raise AssertionError('standalone accepted missing class binding')
        except ValueError as e:
         assert str(e)=='missing or ambiguous Model class binding: NamedSelection'
         print('standalone_changed','rejected',type(e).__name__,str(e))

        owner.write_text(original_owner)
        reader=SourceReader(root);reader.capture()
        duplicate=write('CA-R-990006','ANECHOIC_MODEL <+ Named Selection',binding_body)
        try:
         reader.capture([{'operation':'create','old_path':None,'new_path':duplicate.relative_to(root).as_posix()}]);raise AssertionError('duplicate accepted')
        except ValueError as e:
         assert str(e)=='missing or ambiguous Model class binding: NamedSelection'
         print('reader_duplicate','rejected',str(e))

