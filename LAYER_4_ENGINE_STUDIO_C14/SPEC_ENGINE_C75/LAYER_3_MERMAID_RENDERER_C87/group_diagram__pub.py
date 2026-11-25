from ..LAYER_2_FORMAL_MODEL_C85.group_model__pub import _names


def group_to_mermaid(claim, component_id):
    _names([component_id], r'C[0-9]+', 'group Component ID')
    lines = ['flowchart TD', f'    {component_id}["{component_id}"]']
    lines += [f'    {component_id} -->|{role}| {child}["{child}"]'
              for role, child in claim['roles'].items()]
    return '\n'.join(lines)
