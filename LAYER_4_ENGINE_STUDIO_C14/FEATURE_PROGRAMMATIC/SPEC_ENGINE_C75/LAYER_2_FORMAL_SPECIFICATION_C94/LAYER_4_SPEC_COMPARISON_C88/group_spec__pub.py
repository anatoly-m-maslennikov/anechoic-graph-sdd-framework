from .group_comparison import group_spec__shared as _implementation


def check_group_spec(
    root,
    component_id,
    manifest,
    contract=None,
    solution=None,
    *,
    structure_children,
    role_providers=None,
    current_record_count=None,
    lean="lean",
):
    return _implementation.check_group_spec(
        root,
        component_id,
        manifest,
        contract,
        solution,
        structure_children=structure_children,
        role_providers=role_providers,
        current_record_count=current_record_count,
        lean=lean,
    )
