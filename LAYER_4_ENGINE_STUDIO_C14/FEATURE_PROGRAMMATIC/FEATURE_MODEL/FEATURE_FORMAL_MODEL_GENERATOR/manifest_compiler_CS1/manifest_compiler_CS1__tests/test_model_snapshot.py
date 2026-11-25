from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import (
    ModelSourceError, compile_active_model_rows, read_active_model_sources,
)
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler import build_model_from_rows
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.model_startup import select_model_rows
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier
from .test_active_model_sources import carrier, custom_carrier


def row(path, text, ref):
    parsed = parse_carrier(text.encode(), Path(path))
    return dict(source_path=path, exact_ref=ref, metadata=parsed.metadata, body=parsed.body)


class ModelSnapshotTests(unittest.TestCase):
    def test_rows_match_filesystem_lowering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            path = 'LAYER_1_META_ONTOLOGY_C9/AN-S-1-SPEC--atom.md'
            file = root / path
            file.parent.mkdir()
            file.write_text(carrier())
            custom_path = '002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-MODEL_MANIFEST--node.md'
            custom = root / custom_path
            custom.parent.mkdir(parents=True)
            custom.write_text(custom_carrier())
            rows = [row(path, carrier(), 'AN-S-1@1'), row(custom_path, custom_carrier(), 'AN-C-1@1')]
            self.assertEqual(read_active_model_sources(root, file.parent),
                             compile_active_model_rows(select_model_rows(rows), has_c9=True))

    def test_nested_component_matches_snapshot_and_direct_compilation(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler import write_model
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            component = root / 'ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9'
            component.mkdir(parents=True)
            file = component / 'AN-S-1-SPEC--atom.md'
            file.write_text(carrier())
            path = file.relative_to(root).as_posix()
            rows = [row(path, carrier(), 'AN-S-1@1')]
            self.assertEqual(read_active_model_sources(root, component),
                             compile_active_model_rows(select_model_rows(rows), has_c9=True))
            with patch('FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler.write_model_records') as write:
                write_model(root, root)
                self.assertEqual(write.call_args.args[1], read_active_model_sources(root, component))

    def test_fallback_and_custom_requires_c9(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(compile_active_model_rows([], has_c9=False))
            self.assertTrue(build_model_from_rows(Path(tmp), [], has_c9=False))
        custom = row('__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-MODEL_MANIFEST--node.md', custom_carrier(), 'AN-C-1@1')
        with self.assertRaisesRegex(ValueError, 'require an active C9'):
            compile_active_model_rows([custom], has_c9=False)
        with self.assertRaisesRegex(ValueError, 'No active Model Claims'):
            compile_active_model_rows([], has_c9=True)

    def test_inconsistent_reference_has_structured_context(self):
        path = 'LAYER_1_META_ONTOLOGY_C9/AN-S-1-SPEC--atom.md'
        with self.assertRaises(ModelSourceError) as raised:
            compile_active_model_rows([row(path, carrier(), 'AN-S-1@2')], has_c9=True)
        self.assertEqual((raised.exception.stage, raised.exception.code, raised.exception.atom_ref, raised.exception.source_path),
                         ('model_compile', 'invalid_model_source', 'AN-S-1@2', path))

class EntityAnchorTests(unittest.TestCase):
    def test_missing_parent_reports_exact_source_and_subject(self):
        path = 'LAYER_1_META_ONTOLOGY_C9/AN-S-1-SPEC--child.md'
        subject = 'MODEL//ANECHOIC <+ Node//Missing//Child'
        text = carrier(subject=subject).replace('  lens: SPEC', '  lens: SPEC\n  template: manifest_node')
        text = text[:text.index('## Claim\n')] + '''## Formal Manifest

```python anechoic-edsl
from anechoic.model import Node
class Child(Node):
    pass
```
'''
        with self.assertRaises(ModelSourceError) as raised:
            compile_active_model_rows([row(path, text, 'AN-S-1@1')], has_c9=True)
        error = raised.exception
        self.assertEqual((error.code, error.subject, error.atom_ref, error.source_path),
                         ('missing_entity_parent', subject, 'AN-S-1@1', path))

    def test_native_target_alias_is_an_anchor(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import _check_entity_parent_anchors
        claim = "from anechoic.formal_claims import declare_entity\nclass Parent:\n    pass\ndeclare_entity(entity_name='Parent', entity_class=Parent, entity_kind='Primary')\n"
        root_claim = claim.replace('Parent', 'Node')
        records = [('root.md@1', 'MODEL//ANECHOIC <+ Node', root_claim),
                   ('parent.md@1', 'MODEL//ANECHOIC <+ Node//Parent', claim)]
        _check_entity_parent_anchors(records, [('child.md@1', 'MODEL//ANECHOIC <+ Node//Parent//Child')])

    def test_ambiguous_parent_has_distinct_code(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import _check_entity_parent_anchors
        subject = 'MODEL//ANECHOIC <+ Node//Parent//Child'
        with self.assertRaises(ModelSourceError) as raised:
            _check_entity_parent_anchors([], [('root.md@1', 'MODEL//ANECHOIC <+ Node'),
                                               ('one.md@1', 'MODEL//ANECHOIC <+ Node//Parent'),
                                               ('two.md@1', 'MODEL//ANECHOIC <+ Node//Parent'),
                                               ('child.md@1', subject)])
        self.assertEqual(raised.exception.code, 'ambiguous_entity_parent')
        self.assertEqual(raised.exception.subject, subject)

    def test_containment_requires_parent_and_accepts_unique_native_alias(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.active_model_sources import _check_entity_parent_anchors
        claim = "from anechoic.formal_claims import declare_entity\nclass Package:\n    pass\ndeclare_entity(entity_name='Package', entity_class=Package, entity_kind='Primary')\n"
        root_claim = claim.replace('Package', 'Node')
        artifact_claim = claim.replace('Package', 'Artifact')
        records = [('node.md@1', 'MODEL//ANECHOIC <+ Node', root_claim),
                   ('artifact.md@1', 'MODEL//ANECHOIC <+ Node//Artifact', artifact_claim),
                   ('package.md@1', 'MODEL//ANECHOIC <+ Node//Artifact//Package', claim)]
        _check_entity_parent_anchors(records, [('module.md@1', 'MODEL//ANECHOIC <+ Package/Module')])
        with self.assertRaises(ModelSourceError) as raised:
            _check_entity_parent_anchors(records, [('child.md@1', 'MODEL//ANECHOIC <+ Missing/Child')])
        self.assertEqual(raised.exception.code, 'missing_entity_parent')
        self.assertEqual(raised.exception.subject, 'MODEL//ANECHOIC <+ Missing/Child')

    def test_invalid_custom_typed_node_reports_source(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
        from .test_typed_node_pilot import AXIOM, ROOT
        control = ROOT / '_anechoic_anechoic'
        rows = []
        for directory in (control / 'LAYER_1_META_ONTOLOGY_C9', control / 'LAYER_1_META_ONTOLOGY_C9/_SPEC'):
            if not directory.is_dir():
                continue
            for file in directory.glob('*.md'):
                parsed = parse_carrier(file.read_bytes(), file)
                header = native_header_view(parsed.metadata)
                state, identity = header.get('state') or {}, header.get('identity') or {}
                if state.get('status') == 'active':
                    rows.append(dict(source_path=file.relative_to(control).as_posix(),
                                     exact_ref=f"{identity.get('atom_id')}@{state.get('version')}",
                                     metadata=parsed.metadata, body=parsed.body))
        path = '__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-3193-MANIFEST_NODE--axiom.md'
        rows.append(row(path, AXIOM.replace('Lens.SPEC', 'Lens.UNKNOWN'), 'AN-C-3193@4'))
        with self.assertRaises(ModelSourceError) as raised:
            compile_active_model_rows(rows, has_c9=True)
        error = raised.exception
        self.assertEqual((error.code, error.source_path, error.atom_ref),
                         ('invalid_typed_node', path, 'AN-C-3193@4'))
        self.assertIsNone(error.subject)
        self.assertIn('unsupported typed manifest value', str(error))
        self.assertIn('AN-C-3193@4', str(error))
