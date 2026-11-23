"""Formal-contract graph preserves complete, source-bound Claim evidence."""

from pathlib import Path
import sys


TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph


def carrier(atom_id, active, body, *, role="Requirement", form="Declaration"):
    return {
        "source": {"atom_id": atom_id, "version": 1, "path": f"sources/{atom_id}.md"},
        "subjects": {"active": active, "passive": []}, "body": body,
        "read_view": {"content_role": role, "type": form},
    }

def body(*claim_lines, semantics=None):
    result = "## Claim\n\n" + "\n".join(claim_lines) + "\n"
    if semantics is not None:
        result += "\n## Semantics\n\n" + semantics + "\n"
    return result

def scope_context_graph():
    return compose_contract_graph([
        carrier("CA-R-1", "Scope Unit", body("Scope Unit kind declaration.")),
        carrier("CA-R-2", "Project", body("Project kind declaration.")),
        carrier("CA-R-9", "Projection", body("Projection kind declaration.")),
        carrier("CA-R-10", "Named Selection", body("Selection kind declaration.")),
        carrier("CA-R-11", "ANECHOIC <+ MODEL <+ PROJECT STRUCTURE", body("Structure kind declaration.")),
        carrier("CA-R-3", "Scope Unit//CORE_META_MODEL", body("Core scope declaration."),
                form="Scope Unit Declaration"),
        carrier("CA-R-4", "Project//anechoic", body("Project declaration."),
                form="Scope Unit Declaration"),
        carrier("CA-R-5", "Scope Unit//CORE_META_MODEL", body("Core scope evidence."),
                form="Rule"),
        carrier("CA-R-6", "Project//anechoic", body("Project evidence."), form="Rule"),
        carrier("CA-R-7", "Scope Unit//MISSING", body("Missing scope evidence."), form="Rule"),
        carrier("CA-R-8", "Actor//ANATOLY", body("Unknown kind declaration."),
                form="Scope Unit Declaration"),
        carrier("CA-R-12", "Projection//PROJECT_SCOPE_UNIT_GRAPH", body("Projection context."),
                form="Rule"),
        carrier("CA-R-13", "Named Selection//ExtensionSources", body("Selection context."),
                form="Rule"),
        carrier("CA-R-14", "ANECHOIC <+ STRUCTURE", body("Structure context."),
                form="Rule"),
        carrier("CA-R-15", "Named Selection//Unknown", body("Unknown selection context."),
                form="Rule"),
        carrier("CA-R-16", "PROJECT STRUCTURE//ANECHOIC", body("Historical structure context."),
                form="Rule"),
    ])
