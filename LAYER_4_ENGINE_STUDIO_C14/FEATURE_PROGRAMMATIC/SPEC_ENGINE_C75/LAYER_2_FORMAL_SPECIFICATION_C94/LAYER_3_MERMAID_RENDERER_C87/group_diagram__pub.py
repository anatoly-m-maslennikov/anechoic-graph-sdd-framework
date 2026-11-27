from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import _names


def group_to_mermaid(claim, component_id):
    _names([component_id], r'C[0-9]+', 'group Component ID')
    label = component_id
    if 'current_record_count' in claim:
        label += f" ({claim['current_record_count']} records)"
    lines = ['flowchart TD', f'    {component_id}["{label}"]']
    lines += [f'    {component_id} -->|{role}| {child}["{child}"]'
              for role, child in claim['roles'].items()]
    return '\n'.join(lines)
