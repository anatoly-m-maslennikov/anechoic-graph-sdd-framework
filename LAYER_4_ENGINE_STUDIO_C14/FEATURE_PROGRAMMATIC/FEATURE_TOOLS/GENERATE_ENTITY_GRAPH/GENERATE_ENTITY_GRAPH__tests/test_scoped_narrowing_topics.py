from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_current_graph, compose_narrowing_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.enhanced_graph_test_support import carrier


def declaration(number, subject, name, cls, base=None):
    imported = f'from anechoic.model import {base}\n' if base else ''
    code = (f'from anechoic.formal_claims import declare_entity\n{imported}'
            f'class {cls}' + (f'({base})' if base else '') + ':\n    pass\n'
            f'declare_entity(entity_class={cls}, entity_name={name!r})\n')
    return {'source': {'atom_id': f'CA-R-{number}', 'version': 1, 'path': f'{number}.md'},
            'subjects': {'active': subject}, 'read_view': {'content_role': 'Requirement', 'type': 'Declaration'},
            'body': f'## Claim\n### Formal Claim\n```python\n{code}```\n'}


class ScopedNarrowingTopicsTests(unittest.TestCase):
    def test_structure_containment_is_scoped_to_namespace(self):
        graph, _ = compose_current_graph([
            carrier("CA-R-1", {"active": "ANECHOIC_STRUCTURE/ENGINE/PROGRAMMATIC"}),
            carrier("CA-R-2", {"active": "Node/Continuant"}),
            carrier("CA-R-3", {"active": "Relation//RUNS"}),
        ])
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        self.assertEqual({
            ("ANECHOIC_STRUCTURE/ENGINE", "IS_CONTAINED_BY", "ANECHOIC_STRUCTURE"),
            ("ANECHOIC_STRUCTURE/ENGINE/PROGRAMMATIC", "IS_CONTAINED_BY", "ANECHOIC_STRUCTURE/ENGINE"),
            ("Node/Continuant", "NARROWER_THAN", "Node"),
            ("Relation//RUNS", "INSTANCE_OF", "Relation"),
        }, {
            (names[row["relation_source"]], row["kind"], names[row["relation_target"]])
            for row in graph["edges"]
        })

    def test_native_class_declarations_admit_double_slash_narrowing(self):
        actor = declaration(1, 'ANECHOIC_MODEL <+ Node/Continuant/Actor', 'Actor', 'Actor')
        ai = declaration(2, 'ANECHOIC_MODEL <+ Node//Continuant//Actor//AI Agent', 'AI Agent', 'AIAgent', 'Actor')
        main = declaration(3, 'ANECHOIC_MODEL <+ Node//Continuant//Actor//AI Agent//Main Agent', 'Main Agent', 'MainAgent', 'AIAgent')
        rows = [actor, ai, main]
        graph = compose_contract_graph(rows)
        targets = {row['target'] for row in graph['entities']}
        self.assertIn('Node//Continuant//Actor//AI Agent', targets)
        self.assertIn('Node//Continuant//Actor//AI Agent//Main Agent', targets)
        tree, _ = compose_narrowing_graph(rows)
        identities = {node['id']: node['identity'] for node in tree['nodes']}
        edges = {(identities[e['relation_source']], identities[e['relation_target']]) for e in tree['edges']}
        self.assertIn(('Node//Continuant//Actor//AI Agent', 'Node/Continuant/Actor'), edges)
        self.assertIn(('Node//Continuant//Actor//AI Agent//Main Agent', 'Node//Continuant//Actor//AI Agent'), edges)
        raw, _ = compose_current_graph(rows)
        ids = {node['id']: node['identity'] for node in raw['nodes']}
        self.assertTrue(any(e['kind'] == 'NARROWER_THAN' and ids[e['relation_source']] == 'Node//Continuant//Actor//AI Agent' for e in raw['edges']))


if __name__ == '__main__':
    unittest.main()
