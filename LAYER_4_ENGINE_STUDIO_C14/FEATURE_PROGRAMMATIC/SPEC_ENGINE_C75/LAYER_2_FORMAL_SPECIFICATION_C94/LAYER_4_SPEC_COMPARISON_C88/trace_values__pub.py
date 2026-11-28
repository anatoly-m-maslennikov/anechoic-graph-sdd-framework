from .trace_facts_impl import _package__shared as _implementation


def compare_trace_values(case, events, *, lean="lean"):
    return _implementation.compare_trace_values(case, events, lean=lean)
