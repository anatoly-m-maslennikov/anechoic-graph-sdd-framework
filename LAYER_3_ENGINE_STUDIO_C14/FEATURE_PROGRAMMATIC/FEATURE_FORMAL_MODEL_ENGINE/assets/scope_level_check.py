SOURCE_REFERENCE = 'CA-R-2554@3'
SOURCE_SHA256 = '9b336b083bc609371b69a897056f889f8d376945354e687b332a3f57803e3036'
CLAIM_SHA256 = '6622c5367e605ec900c303a04800658d9aea18daccdb900f9650eadc06408058'
from FEATURE_FORMAL_MODEL_ENGINE.scope_levels import ScopeUnit

def check_structural_level(unit: ScopeUnit) -> bool:
    if unit.structural_level is None:
        return False
    if unit.container is None:
        return unit.structural_level == 0
    return (
        unit.container.structural_level is not None
        and unit.structural_level == unit.container.structural_level + 1
    )
