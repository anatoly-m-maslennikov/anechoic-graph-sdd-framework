from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared \
    import normalize_workflow  # fmt: skip
from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_MERMAID_RENDERER_C87.\
    _package__shared \
    import render_workflow_diagram  # fmt: skip


def compile_workflow(config):
    model = normalize_workflow(config)
    return {"model": model, "mermaid": render_workflow_diagram(model)}
