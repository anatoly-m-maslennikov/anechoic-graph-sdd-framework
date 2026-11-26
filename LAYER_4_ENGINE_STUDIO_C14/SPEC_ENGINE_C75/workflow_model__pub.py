from .LAYER_2_FORMAL_MODEL_C85.workflow_model__pub import normalize_workflow
from .LAYER_3_MERMAID_RENDERER_C87.workflow_diagram__pub import render_workflow_diagram


def compile_workflow(config):
    model = normalize_workflow(config)
    return {"model": model, "mermaid": render_workflow_diagram(model)}
