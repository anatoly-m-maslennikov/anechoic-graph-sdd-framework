"""Bind the Work Report Task Relation from the selected native Declarations."""

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_GENERATED_MODEL_C52.FEATURE_GENERATED_MODEL_C52__shared import (
    Plan, PlanForm, WorkReport,
)
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.cardinality__pub import cardinality_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import header_value

RELATION = "IS_WORK_REPORT_FOR"
TASK_PATH = "Atom/(.Header.Context.Role:=Plan)/(.Header.Context.Form:=Plan)"


def compile_work_report_target(rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import iter_formal_claims
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim

    declarations = []
    for row in rows:
        for code in iter_formal_claims(row["_content_bytes"].decode("utf-8")):
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
    if (not isinstance(constraint, dict) or set(constraint) != {"targets_per_source", "target_entity_paths"}
            or constraint["target_entity_paths"] not in ([TASK_PATH], (TASK_PATH,))
            or cardinality_bounds(constraint["targets_per_source"]) != (1, 1)):
        raise ValueError(f"{RELATION} must select exactly one Plan Form target")
