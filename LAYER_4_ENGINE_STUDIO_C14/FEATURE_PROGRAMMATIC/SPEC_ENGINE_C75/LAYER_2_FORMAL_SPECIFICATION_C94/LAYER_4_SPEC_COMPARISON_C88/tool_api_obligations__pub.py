from .tool_obligations import tool_api_obligations__shared as _implementation


def manifest_tool_api(api):
    return _implementation.manifest_tool_api(api)


def contract_tool_api(claim):
    return _implementation.contract_tool_api(claim)


def solution_tool_api(claim, expected=None):
    return _implementation.solution_tool_api(claim, expected)
