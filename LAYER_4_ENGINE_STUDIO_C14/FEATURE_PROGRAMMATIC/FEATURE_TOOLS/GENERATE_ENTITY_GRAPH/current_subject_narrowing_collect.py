"""Build declared narrowing graph phases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    carrier_read_view,
    matches_named_value,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    claim_constraints import (
    extract_claim_constraints,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    current_subject_common import (
    Record,
    _identifier,
    _target_kind,
    _view,
    namespace_local_expression,
    subject_facts,
    _NAMESPACE_ROOTS,
)  # fmt: skip


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    current_subject_relation_paths import NarrowingRelationPaths  # fmt: skip


class NarrowingCollection(NarrowingRelationPaths):
    def __init__(self):
        self.nodes: dict[str, Record] = {}
        self.edges: dict[str, Record] = {}
        self.diagnostics: list[str] = []
        self.pending: list[tuple[str, str, str, bool]] = []
        self.owners: list[Record] = []
        self.declaration_targets: list[tuple[Record, str]] = []
        self.native_classes: list[tuple[Record, str, Record]] = []

    def source_name(self, carrier: Record) -> str:
        source = carrier["source"]
        return f"{source['atom_id']}@{source['version']}"

    def claim_constraints(self, carrier: Record) -> list[Record]:
        constraints, claim_diagnostics = extract_claim_constraints(carrier)
        for diagnostic in claim_diagnostics:
            if diagnostic["code"] == "python-formal-claim-invalid":
                raise ValueError(
                    f"{self.source_name(carrier)}: {diagnostic['message']}"
                )  # fmt: skip
        return constraints

    def active(self, carrier: Record) -> str | None:
        subjects = carrier.get("subjects")
        if not isinstance(subjects, dict):
            self.diagnostics.append(
                f"{self.source_name(carrier)}: active Subject is unavailable."
            )
            return None
        try:
            value = carrier_read_view({"subjects": subjects})["subjects"].get(
                "governs"
            )
        except ValueError as error:
            self.diagnostics.append(f"{self.source_name(carrier)}: {error}")
            return None
        values = value if isinstance(value, list) else [value]
        if (
            len(values) != 1
            or not isinstance(values[0], str)
            or (not values[0].strip())
        ):
            self.diagnostics.append(
                f"{self.source_name(carrier)}: "
                "exactly one active Subject is required."
            )
            return None
        return values[0]

    def label(self, expression: _subject_Path, canonical: str) -> str:
        if not expression.steps:
            return canonical
        operand = expression.steps[-1].operand
        if isinstance(operand, _subject_Name):
            return operand.value
        if isinstance(operand, _subject_Qualification):
            return "(." + _subject_render_subject(operand.relative_path) + ")"
        return canonical

    def add_node(
        self, identity: str, display_name: str, carrier: Record
    ) -> None:
        key = _identifier("narrowing:", identity)
        node = self.nodes.setdefault(
            key,
            {
                "id": key,
                "identity": identity,
                "display_name": display_name,
                "source_bindings": set(),
            },
        )
        node["source_bindings"].add(self.source_name(carrier))

    def add_path(
        self,
        carrier: Record,
        subject: str,
        *,
        retained_relation_root: bool = False,
        native_class: bool = False,
    ) -> bool:
        parsed, expression = self._parse_path(carrier, subject)
        if not parsed:
            return False
        local_expression = namespace_local_expression(expression)
        if local_expression is not None:
            expression = local_expression
            subject = _subject_render_subject(expression)
        if not isinstance(expression, _subject_Path):
            return self.add_relation_path(
                carrier, subject, expression, retained_relation_root
            )
        if (
            isinstance(expression.head, _subject_Name)
            and expression.head.value in _NAMESPACE_ROOTS
            and (not expression.steps)
        ):
            return True
        if _target_kind(expression) in {"property", "instance"} and (
            not native_class
        ):
            return True
        if _target_kind(expression) != "primary_node" and (not native_class):
            self.diagnostics.append(
                f"{self.source_name(carrier)}: Subject `{subject}` "
                "does not declare one Primary Node."
            )
            return False
        result = self._path_facts(carrier, subject, native_class)
        if result is None:
            return False
        facts, target = result
        self._record_path(carrier, expression, target, facts, native_class)
        return True

    def _parse_path(self, carrier, subject):
        try:
            expression = _subject_parse_subject_expression(
                subject, subject_profile="approved"
            ).expression
        except _subject_SubjectNotationError as error:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: "
                f"unsupported Subject `{subject}`: {error}."
            )
            return False, None
        return True, expression

    def _path_facts(self, carrier, subject, native_class):
        try:
            _, facts, target = subject_facts(
                subject, native_class_narrowing=native_class
            )
        except (_subject_SubjectNotationError, ValueError) as error:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: "
                f"Subject facts unavailable: {error}."
            )
            return None
        return facts, target

    def _record_path(self, carrier, expression, target, facts, native_class):
        self.add_node(target, self.label(expression, target), carrier)
        for fact in () if native_class else facts:
            if fact["kind"] == "NARROWER_THAN":
                self.pending.append(
                    (
                        fact["source"],
                        fact["target"],
                        self.source_name(carrier),
                        False,
                    )
                )

    def collect_declaration(self, carrier, subject):
        constraints = self.claim_constraints(carrier)
        native = [
            row for row in constraints if row.get("kind") == "native_class"
        ]
        if len(native) > 1:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: "
                "multiple native class declarations."
            )
            return
        try:
            expression = _subject_parse_subject_expression(
                subject, subject_profile="approved"
            ).expression
        except _subject_SubjectNotationError:
            expression = None
        expression = namespace_local_expression(expression) or expression
        if isinstance(
            expression, _subject_RelationChain
        ) and self.add_cfel_component_endpoint(carrier, expression):
            self.owners.append(carrier)
            return
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            ADAPTERS_C30__shared import (
            model_class_target,
        )  # fmt: skip

        native_class = bool(
            native
            and model_class_target(
                subject, native[0].get("entity_name"), require_namespace=False
            )
        )
        if self.add_path(carrier, subject, native_class=native_class):
            self.owners.append(carrier)
            self._register_declaration(carrier, subject, native_class, native)
        return

    def _register_declaration(self, carrier, subject, native_class, native):
        try:
            expression = _subject_parse_subject_expression(
                subject, subject_profile="approved"
            ).expression
            expression = namespace_local_expression(expression) or expression
            if isinstance(expression, _subject_Path) and (
                _target_kind(expression) == "primary_node" or native_class
            ):
                target = _subject_render_subject(expression)
                if native_class:
                    self.native_classes.append((carrier, target, native[0]))
                else:
                    self.declaration_targets.append((carrier, target))
        except _subject_SubjectNotationError:
            pass

    def collect_carrier(self, carrier):
        view = _view(carrier)
        if not matches_named_value(view.get("content_role"), "Requirement"):
            return
        form = view.get("type")
        if not any(
            (
                matches_named_value(form, name)
                for name in {"Declaration", "Entity Definition"}
            )
        ):
            return
        subject = self.active(carrier)
        if subject is None:
            return
        if matches_named_value(form, "Declaration"):
            return self.collect_declaration(carrier, subject)
        if not matches_named_value(form, "Entity Definition"):
            return
        self.collect_definition(carrier, subject)

    def collect_definition(self, carrier, subject):
        try:
            expression = _subject_parse_subject_expression(
                subject, subject_profile="approved"
            ).expression
        except _subject_SubjectNotationError as error:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: retained Entity Definition "
                f"`{subject}` is unsupported: {error}."
            )
            return
        expression = namespace_local_expression(expression) or expression
        if isinstance(expression, _subject_RelationChain):
            if self.add_cfel_component_endpoint(carrier, expression):
                self.owners.append(carrier)
                return
            if self.add_path(carrier, subject, retained_relation_root=True):
                self.owners.append(carrier)
            return
        if not isinstance(
            expression.head, _subject_Name
        ) or expression.head.value not in {"CFEL", "Carrier", "Term"}:
            self.diagnostics.append(
                f"{self.source_name(carrier)}: Entity Definition `{subject}` "
                "is outside retained CFEL, Carrier, Term roots."
            )
            return
        if self.add_path(carrier, subject):
            self.owners.append(carrier)

    def collect(self, carriers):
        for carrier in carriers:
            self.collect_carrier(carrier)
