"""Render the admitted Solution claim."""

from .framing_diagram__pub import framing_to_mermaid
from .group_diagram__pub import group_to_mermaid
from .shape_diagram__pub import shape_to_mermaid
from .workflow_diagram__pub import render_operation_diagram, render_workflow_diagram


def render_solution(model, claim):
    if claim is None:
        return None
    language = model['solution']['claims'][0][0]
    if language == 'python framing':
        return framing_to_mermaid(claim)
    if language == 'python group':
        return group_to_mermaid(claim, model['component_id'])
    if language == 'python shape':
        return shape_to_mermaid(claim)
    if 'operations' in claim:
        return render_operation_diagram(claim['operations'])
    return render_workflow_diagram(claim)
