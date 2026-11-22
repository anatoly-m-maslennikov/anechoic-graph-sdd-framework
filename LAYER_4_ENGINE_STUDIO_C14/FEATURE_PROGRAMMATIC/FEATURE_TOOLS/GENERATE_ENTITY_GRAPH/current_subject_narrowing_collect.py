"""Build declared narrowing graph phases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view, matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import (
    Record, _identifier, _target_kind, _view, namespace_local_expression,
    subject_facts, _NAMESPACE_ROOTS,
)


class NarrowingCollection:

    def __init__(self):
        self.nodes: dict[str, Record] = {}
        self.edges: dict[str, Record] = {}
        self.diagnostics: list[str] = []
        self.pending: list[tuple[str, str, str, bool]] = []
        self.owners: list[Record] = []
        self.declaration_targets: list[tuple[Record, str]] = []
        self.native_classes: list[tuple[Record, str, Record]] = []

    def source_name(self, carrier: Record) -> str:
        source = carrier['source']
        return f"{source['atom_id']}@{source['version']}"

    def claim_constraints(self, carrier: Record) -> list[Record]:
        constraints, claim_diagnostics = extract_claim_constraints(carrier)
        for diagnostic in claim_diagnostics:
            if diagnostic['code'] == 'python-formal-claim-invalid':
                raise ValueError(f"{self.source_name(carrier)}: {diagnostic['message']}")
        return constraints

    def active(self, carrier: Record) -> str | None:
        subjects = carrier.get('subjects')
        if not isinstance(subjects, dict):
            self.diagnostics.append(f'{self.source_name(carrier)}: active Subject is unavailable.')
            return None
        try:
            value = carrier_read_view({'subjects': subjects})['subjects'].get('governs')
        except ValueError as error:
            self.diagnostics.append(f'{self.source_name(carrier)}: {error}')
            return None
        values = value if isinstance(value, list) else [value]
        if len(values) != 1 or not isinstance(values[0], str) or (not values[0].strip()):
            self.diagnostics.append(f'{self.source_name(carrier)}: exactly one active Subject is required.')
            return None
        return values[0]

    def label(self, expression: notation.Path, canonical: str) -> str:
        if not expression.steps:
            return canonical
        operand = expression.steps[-1].operand
        if isinstance(operand, notation.Name):
            return operand.value
        if isinstance(operand, notation.Qualification):
            return '(.' + notation.render_subject(operand.relative_path) + ')'
        return canonical

    def add_node(self, identity: str, display_name: str, carrier: Record) -> None:
        key = _identifier('narrowing:', identity)
        node = self.nodes.setdefault(key, {'id': key, 'identity': identity, 'display_name': display_name, 'source_bindings': set()})
        node['source_bindings'].add(self.source_name(carrier))

    def add_cfel_component_endpoint(self, carrier: Record, expression: notation.RelationChain) -> bool:
        """Admit the explicitly declared CFEL component, never its composition edge."""
        if len(expression.endpoints) != 2 or len(expression.links) != 1:
            return False
        left, right = expression.endpoints
        link = expression.links[0]
        if link.operator != '<+' or link.relation_type is not None or (not isinstance(left.head, notation.Name)) or (left.head.value != 'CFEL'):
            return False
        kind = _target_kind(right)
        if kind in {'property', 'instance', 'relation'}:
            return True
        if kind != 'primary_node':
            return False
        try:
            _, facts, target = subject_facts(notation.render_subject(right))
        except (notation.SubjectNotationError, ValueError) as error:
            self.diagnostics.append(f'{self.source_name(carrier)}: CFEL component endpoint is unsupported: {error}.')
            return False
        self.add_node(target, self.label(right, target), carrier)
        for fact in facts:
            if fact['kind'] == 'NARROWER_THAN':
                self.pending.append((fact['source'], fact['target'], self.source_name(carrier), False))
        return True

    def add_relation_path(self, carrier, subject, expression, retained_relation_root):
        first = expression.endpoints[0].head
        if not retained_relation_root or not isinstance(first, notation.Name) or first.value not in {'CFEL', 'Carrier', 'Term'}:
            self.diagnostics.append(f'{self.source_name(carrier)}: relation Subject `{subject}` is outside retained roots.')
            return False
        try:
            supplied, facts, _ = subject_facts(subject)
        except (notation.SubjectNotationError, ValueError) as error:
            self.diagnostics.append(f'{self.source_name(carrier)}: unsupported relation Subject `{subject}`: {error}.')
            return False
        references = {row['identity'] for row in supplied if row.get('declared_reference')}
        for fact in facts:
            if fact['kind'] == 'NARROWER_THAN':
                self.pending.append((fact['source'], fact['target'], self.source_name(carrier), fact['target'] in references))
        return True

    def add_path(self, carrier: Record, subject: str, *, retained_relation_root: bool=False, native_class: bool=False) -> bool:
        try:
            expression = notation.parse_subject_expression(subject, subject_profile='approved').expression
        except notation.SubjectNotationError as error:
            self.diagnostics.append(f'{self.source_name(carrier)}: unsupported Subject `{subject}`: {error}.')
            return False
        local_expression = namespace_local_expression(expression)
        if local_expression is not None:
            expression = local_expression
            subject = notation.render_subject(expression)
        if not isinstance(expression, notation.Path):
            return self.add_relation_path(carrier, subject, expression, retained_relation_root)
        if isinstance(expression.head, notation.Name) and expression.head.value in _NAMESPACE_ROOTS and (not expression.steps):
            return True
        if _target_kind(expression) in {'property', 'instance'} and (not native_class):
            return True
        if _target_kind(expression) != 'primary_node' and (not native_class):
            self.diagnostics.append(f'{self.source_name(carrier)}: Subject `{subject}` does not declare one Primary Node.')
            return False
        try:
            _, facts, target = subject_facts(subject, native_class_narrowing=native_class)
        except (notation.SubjectNotationError, ValueError) as error:
            self.diagnostics.append(f'{self.source_name(carrier)}: Subject facts unavailable: {error}.')
            return False
        self.add_node(target, self.label(expression, target), carrier)
        for fact in () if native_class else facts:
            if fact['kind'] == 'NARROWER_THAN':
                self.pending.append((fact['source'], fact['target'], self.source_name(carrier), False))
        return True

    def collect_declaration(self, carrier, subject):
        constraints = self.claim_constraints(carrier)
        native = [row for row in constraints if row.get('kind') == 'native_class']
        if len(native) > 1:
            self.diagnostics.append(f'{self.source_name(carrier)}: multiple native class declarations.')
            return
        try:
            expression = notation.parse_subject_expression(subject, subject_profile='approved').expression
        except notation.SubjectNotationError:
            expression = None
        expression = namespace_local_expression(expression) or expression
        if isinstance(expression, notation.RelationChain) and self.add_cfel_component_endpoint(carrier, expression):
            self.owners.append(carrier)
            return
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import model_class_target
        native_class = bool(native and model_class_target(subject, native[0].get('entity_name'), require_namespace=False))
        if self.add_path(carrier, subject, native_class=native_class):
            self.owners.append(carrier)
            try:
                expression = notation.parse_subject_expression(subject, subject_profile='approved').expression
                expression = namespace_local_expression(expression) or expression
                if isinstance(expression, notation.Path) and (_target_kind(expression) == 'primary_node' or native_class):
                    target = notation.render_subject(expression)
                    if native_class:
                        self.native_classes.append((carrier, target, native[0]))
                    else:
                        self.declaration_targets.append((carrier, target))
            except notation.SubjectNotationError:
                pass
        return

    def collect_carrier(self, carrier):
        view = _view(carrier)
        if not matches_named_value(view.get('content_role'), 'Requirement'):
            return
        form = view.get('type')
        if not any((matches_named_value(form, name) for name in {'Declaration', 'Entity Definition'})):
            return
        subject = self.active(carrier)
        if subject is None:
            return
        if matches_named_value(form, 'Declaration'):
            return self.collect_declaration(carrier, subject)
        if not matches_named_value(form, 'Entity Definition'):
            return
        try:
            expression = notation.parse_subject_expression(subject, subject_profile='approved').expression
        except notation.SubjectNotationError as error:
            self.diagnostics.append(f'{self.source_name(carrier)}: retained Entity Definition `{subject}` is unsupported: {error}.')
            return
        expression = namespace_local_expression(expression) or expression
        if isinstance(expression, notation.RelationChain):
            if self.add_cfel_component_endpoint(carrier, expression):
                self.owners.append(carrier)
                return
            if self.add_path(carrier, subject, retained_relation_root=True):
                self.owners.append(carrier)
            return
        if not isinstance(expression.head, notation.Name) or expression.head.value not in {'CFEL', 'Carrier', 'Term'}:
            self.diagnostics.append(f'{self.source_name(carrier)}: Entity Definition `{subject}` is outside retained CFEL, Carrier, Term roots.')
            return
        if self.add_path(carrier, subject):
            self.owners.append(carrier)

    def collect(self, carriers):
        for carrier in carriers:
            self.collect_carrier(carrier)
