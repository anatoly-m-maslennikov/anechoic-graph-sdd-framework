import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.typed_manifest_node import parse_typed_manifest_node


AXIOM = '''from anechoic.formal_claims import value
from anechoic.model import Lens, Project, SpecAtom
class Axiom(SpecAtom):
    tier = value(fixed=0)
    lens = value(fixed=Lens.SPEC)
    container_type = value(fixed=Project)
'''


class TypedManifestNodeTests(unittest.TestCase):
    def test_axiom_static_values(self):
        self.assertEqual(parse_typed_manifest_node(AXIOM), {
            'name': 'Axiom', 'bases': ('SpecAtom',), 'identity': None, 'classifications': None,
            'values': {'tier': ('fixed', 0), 'lens': ('fixed', 'SPEC'),
                       'container_type': ('fixed', ('type', 'Project'))},
        })
        self.assertEqual(parse_typed_manifest_node(AXIOM.replace('fixed=0', 'default=0'))['values']['tier'], ('default', 0))

    def test_signed_numeric_values(self):
        source = AXIOM.replace('tier = value(fixed=0)', 'tier = value(fixed=-1)')
        self.assertEqual(parse_typed_manifest_node(source)['values']['tier'], ('fixed', -1))

    def test_dotted_node_assignments_use_existing_fields(self):
        flat = AXIOM + (
            "    identity = header.atom_id\n"
            "    classifications = {'Temporal Kind': 'Continuant'}\n"
            "    lens_path = value(fixed='SPEC')\n"
            "    control_flow = value(default='Declarative')\n"
        )
        dotted = flat.replace('\n    ', '\n    node.')
        self.assertEqual(parse_typed_manifest_node(dotted), parse_typed_manifest_node(flat))
        for source in (
            dotted + '    tier = value(fixed=1)\n',
            dotted + '    identity = header.atom_id\n',
            dotted + "    classifications = {'Temporal Kind': 'Continuant'}\n",
            dotted.replace('node.tier', 'node.unknown'),
            dotted.replace('node.tier', 'node.extra.tier'),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_typed_manifest_node(source)

    def test_rejects_unadmitted_syntax(self):
        for source in (
            AXIOM.replace('Lens.SPEC', 'Lens.UNKNOWN'),
            AXIOM.replace('fixed=0', 'fixed=print("unsafe")'),
            AXIOM + '\nprint("unsafe")\n',
            AXIOM.replace('fixed=0', 'fixed=0, default=1'),
            AXIOM.replace('from anechoic.model import Lens, Project, SpecAtom', 'from anechoic.model import Lens, Project'),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_typed_manifest_node(source)

    def test_node_constraint_uses_imported_types(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_constraints import lower_node_constraints
        text = "from anechoic.model import NodeConstraints, Atom, Project\nclass Constraints(NodeConstraints):\n    bearer = Atom\n    instance_relation_constraints = {'IS_CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}\n"
        addresses = {'Atom': 'Node//Artifact//Atom', 'Project': 'Node//Artifact//Component//Project'}
        scope = 'MODEL//ANECHOIC <+ Node//Artifact//Atom.Constraints'
        claim = lower_node_constraints(text, scope, addresses)
        self.assertIn("Node//Artifact//Component//Project", claim)
        flat = text + (
            "    model_relation_constraints = {'IS_PROPERTY_OF': {'targets_per_source': 0}}\n"
            "    population_unique_constraints = ({'keys': ('Ref ID',)},)\n"
            "    instance_check = check_atom_identity\n"
        )
        dotted = (flat.replace('instance_relation_constraints =', 'node.constraints.instance_relations =')
                  .replace('model_relation_constraints =', 'node.constraints.model_relations =')
                  .replace('population_unique_constraints =', 'node.constraints.population_unique =')
                  .replace('instance_check =', 'node.constraints.instance_check ='))
        self.assertEqual(lower_node_constraints(dotted, scope, addresses), lower_node_constraints(flat, scope, addresses))
        for source in (
            dotted + '    instance_relation_constraints = {}\n',
            dotted.replace('node.constraints.instance_relations', 'node.constraints.instance_relation_constraints'),
            dotted.replace('bearer = Atom', 'node.constraints.bearer = Atom'),
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                lower_node_constraints(source, scope, addresses)
        with self.assertRaises(ValueError):
            lower_node_constraints(text.replace('(Project,)', "('Project',)"), scope, addresses)
