import json
import unittest

import duckdb

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.model_projection import (
    ensure_model_tables, replace_model_diagnostics, replace_model_projection,
)


def entity(subject, name):
    return [f'MODEL//ANECHOIC <+ {subject}', {'kind': 'entity', 'arguments': {
        'entity_name': name, 'entity_class': name.replace(' ', '')}}]


def prop(subject, name, bearer, **options):
    return [f'MODEL//ANECHOIC <+ {subject}', {'kind': 'entity', 'arguments': {
        'entity_kind': 'Property', 'entity_name': name, 'base_path': bearer, **options}}]


class ModelProjectionTests(unittest.TestCase):
    def test_projects_declared_hierarchy_and_explicit_refinements(self):
        db = duckdb.connect(':memory:')
        ensure_model_tables(db)
        declarations = [entity('Node', 'Node'), entity('Node//Artifact', 'Artifact'),
                        entity('Node//Artifact//Atom', 'Atom'), entity('Atom/Spec', 'Spec'),
                        prop('Node//Artifact//Atom.ID', 'ID', 'Node//Artifact//Atom'),
                        prop('Atom/Spec.ID', 'ID', 'Node//Artifact//Atom',
                             applies_to_entity_classes=['Atom/Spec'], allowed_values=['A'])]
        replace_model_projection(db, {'bindings': {'declarations': declarations}})
        assert db.execute("SELECT parent_path, parent_operator FROM mrt_model_entities WHERE entity_name = 'Spec'").fetchone() == ('Node//Artifact//Atom', '/')
        rows = db.execute('SELECT declaring_node, property_path, refinements, attributes FROM mrt_model_properties ORDER BY subject').fetchall()
        assert len(rows) == 2
        refined = next(row for row in rows if json.loads(row[2]))
        assert refined[:2] == ('Atom/Spec', 'Atom/Spec.ID')
        assert json.loads(refined[3])['base_path'] == 'Node//Artifact//Atom'
        assert json.loads(refined[2]) == ['Atom/Spec']
        assert json.loads(refined[3])['allowed_values'] == ['A']
        replace_model_projection(db, {'bindings': {}})
        assert db.execute('SELECT count(*) FROM mrt_model_entities').fetchone()[0] == 0


    def test_declared_relations_and_full_property_owner(self):
        db = duckdb.connect(':memory:')
        ensure_model_tables(db)
        declarations = [entity('Graph/Relation', 'Relation'),
                        entity('Graph/Structure/Component', 'Component'),
                        entity('Graph/Other/Component', 'Component'),
                        prop('Structure/Component.Tier', 'Tier', 'Graph/Other/Component'),
                        ['MODEL//ANECHOIC <+ Relation//IS_CHILD_OF',
                         {'kind': 'relation', 'arguments': {'relation_name': 'IS_CHILD_OF',
                                                           'inverse_alias': 'IS_PARENT_FOR'}}]]
        replace_model_projection(db, {'bindings': {'declarations': declarations}})
        assert db.execute("SELECT entity_path, parent_path, parent_operator FROM mrt_model_entities "
                          "WHERE entity_name = 'IS_CHILD_OF'").fetchall() == [
                              ('Graph/Relation//IS_CHILD_OF', 'Graph/Relation', '//')]
        assert db.execute("SELECT count(*) FROM mrt_model_entities WHERE entity_name = 'IS_PARENT_FOR'").fetchone()[0] == 0
        assert db.execute('SELECT declaring_node, property_path FROM mrt_model_properties').fetchone() == (
            'Graph/Structure/Component', 'Graph/Structure/Component.Tier')

    def test_relation_parent_uses_legacy_declared_root(self):
        db = duckdb.connect(':memory:')
        ensure_model_tables(db)
        declarations = [entity('Relation', 'Relation'),
                        ['MODEL//ANECHOIC <+ Relation//APPLIES',
                         {'kind': 'relation', 'arguments': {'relation_name': 'APPLIES'}}]]
        replace_model_projection(db, {'bindings': {'declarations': declarations}})
        assert db.execute("SELECT entity_path, parent_path FROM mrt_model_entities WHERE entity_name = 'APPLIES'").fetchone() == (
            'Relation//APPLIES', 'Relation')

    def test_relation_classification_axes_preserve_declared_scopes(self):
        db = duckdb.connect(':memory:')
        ensure_model_tables(db)
        declarations = [entity('Graph/Relation', 'Relation')]
        for axis in ('Functional', 'Transitive'):
            declarations.append([f'MODEL//ANECHOIC <+ Graph/Relation >| {axis}',
                                 {'kind': 'entity', 'arguments': {'entity_name': 'Relation',
                                  'allowed_classification_values': {axis: ['yes', 'no']}}}])
        replace_model_projection(db, {'bindings': {'declarations': declarations}})
        rows = db.execute('SELECT subject, declaring_node, property_path, entity_name, attributes '
                          'FROM mrt_model_properties ORDER BY entity_name').fetchall()
        assert len(rows) == 2
        for row, axis in zip(rows, ('Functional', 'Transitive')):
            assert row[:4] == (f'MODEL//ANECHOIC <+ Graph/Relation >| {axis}', 'Graph/Relation',
                               f'Graph/Relation >| {axis}', axis)
            assert json.loads(row[4])['allowed_classification_values'] == {axis: ['yes', 'no']}

    def test_diagnostics_replace_latest_attempt_without_changing_projection(self):
        db = duckdb.connect(':memory:')
        ensure_model_tables(db)
        replace_model_projection(db, {'bindings': {'declarations': [entity('Node', 'Node')]}})
        row = {'attempt_id': 'try-2', 'accepted_generation': 'gen-1', 'severity': 'error',
               'code': 'invalid', 'message': 'broken', 'atom_ref': 'AN-S-1@1', 'source_path': 'x.md'}
        replace_model_diagnostics(db, [row])
        assert db.execute('SELECT attempt_id, accepted_generation, atom_ref, source_path FROM mrt_diag_model_manifests').fetchone() == ('try-2', 'gen-1', 'AN-S-1@1', 'x.md')
        assert db.execute('SELECT entity_name FROM mrt_model_entities').fetchone() == ('Node',)
        replace_model_diagnostics(db, [])
        assert db.execute('SELECT count(*) FROM mrt_diag_model_manifests').fetchone()[0] == 0
