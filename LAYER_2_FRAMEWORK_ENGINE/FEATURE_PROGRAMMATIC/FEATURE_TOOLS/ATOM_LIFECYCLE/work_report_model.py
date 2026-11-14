"""Bind the Work Report Task Relation from the selected native Declarations."""

from FEATURE_MODEL.FEATURE_GENERATED_MODEL import Plan, PlanForm, WorkReport
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import _bounds, _check_count
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_validation import validate_relation_targets
from header_groups import header_value

RELATION = "IS_WORK_REPORT_FOR"
TASK_PATH = "Atom/(.Header.Context.Role:=Plan)/(.Header.Context.Form:=Plan)"


def compile_work_report_target(rows):
    from FEATURE_FORMAL_MODEL_ENGINE.model_catalog import _native_block
    from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim

    declarations = []
    for row in rows:
        for code in _native_block(row["_content_bytes"].decode("utf-8")):
            claim = parse_native_model_claim(code)
            if claim and claim["arguments"].get("entity_class") in {"PlanForm", "WorkReport"}:
                _, subject = header_value(row["header_json"], "topics.main_subject")
                declarations.append((subject, claim))
    if not any(claim["arguments"]["entity_class"] == "WorkReport" for _, claim in declarations):
        return None
    classes = {kind.__name__: kind for kind in (Plan, PlanForm, WorkReport)}
    relations, types, _ = bind_model_declarations(declarations, classes)
    constraint = relations[WorkReport].get(RELATION)
    if not constraint:
        raise ValueError(f"Work Report Declaration requires a {RELATION} constraint")
    verify_work_report_target(constraint)
    paths = constraint["target_entity_paths"]
    if any(types[path] is not PlanForm for path in paths):
        raise ValueError(f"{RELATION} must target the Plan Form")
    return constraint


def verify_work_report_target(constraint):
    # shortcut: this adapter resolves one Task reference, revisit for other endpoint shapes.
    if (not isinstance(constraint, dict) or set(constraint) != {"targets_per_source", "target_entity_paths"}
            or constraint["target_entity_paths"] not in ([TASK_PATH], (TASK_PATH,))
            or _bounds(constraint["targets_per_source"]) != (1, 1)):
        raise ValueError(f"{RELATION} must select exactly one Plan Form target")


def validate_work_report_target_count(targets, constraint):
    _check_count(RELATION, "target", len(targets), constraint["targets_per_source"])


def validate_work_report_targets(targets, constraint):
    validate_relation_targets(RELATION, targets, constraint, {TASK_PATH: PlanForm}, allow_model_targets=True)
