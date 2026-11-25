"""Mixed Model paths preserve declared class and Property bindings."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    assemble_model_classes,
)
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import (
    bind_model_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    model_class_target,
    parse_native_model_claim,
)


def primary(name, base=None):
    imports = f'from anechoic.model import {base}\n' if base else ''
    signature = f'({base})' if base else ''
    return (f'from anechoic.formal_claims import declare_entity\n{imports}'
            f'class {name}{signature}:\n    pass\n'
            f"declare_entity(entity_name='{name}', entity_class={name}, entity_kind='Primary')\n")


class MixedModelPathsTests(unittest.TestCase):
    def test_class_targets_accept_mixed_and_legacy_paths(self):
        for path in ('Graph/Node//Artifact//Atom', 'Carrier//Document', 'Node//Artifact//Atom'):
            name = path.rsplit('//', 1)[-1]
            with self.subTest(path=path):
                self.assertEqual(model_class_target('MODEL//ANECHOIC <+ ' + path, name), path)
                self.assertIsNone(model_class_target('MODEL//ANECHOIC <+ ' + path, 'Other'))

    def test_property_owners_support_both_path_forms_and_reject_ambiguity(self):
        for path in ('Graph/Node//Artifact//Widget', 'Node//Artifact//Widget'):
            prop = ("from anechoic.formal_claims import declare_entity\n"
                    f"declare_entity(entity_name='Code', entity_kind='Property', relation_name='IS_PROPERTY_OF', base_path={path!r}, value_format=str)\n")
            source = assemble_model_classes([primary('Widget'), prop])
            self.assertIn('code:', source)
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                assemble_model_classes([primary('Widget'), primary('Other').replace("entity_name='Other'", "entity_name='Widget'"), prop])

    def test_runtime_binding_registers_exact_mixed_endpoint(self):
        class Atom:
            pass
        subject = 'MODEL//ANECHOIC <+ Graph/Node//Artifact//Atom'
        claim = primary('Atom').replace("entity_kind='Primary'", "entity_kind='Primary', instance_relation_constraints={'LINKS': {'target_entity_paths': ('Graph/Node//Artifact//Atom',), 'targets_per_source': 1}}")
        declaration = parse_native_model_claim(claim)
        _, types, _ = bind_model_declarations([(subject, declaration)], {'Atom': Atom})
        self.assertIs(types['Graph/Node//Artifact//Atom'], Atom)
        self.assertIs(types['Atom'], Atom)


if __name__ == '__main__':
    unittest.main()
