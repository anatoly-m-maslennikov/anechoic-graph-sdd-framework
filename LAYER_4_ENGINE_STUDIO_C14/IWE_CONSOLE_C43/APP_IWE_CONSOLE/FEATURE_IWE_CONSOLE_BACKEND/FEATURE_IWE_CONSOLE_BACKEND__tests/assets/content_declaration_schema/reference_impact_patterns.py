"""Patterns and reviewed paths for the prepared Header migration."""
import json
import re
from pathlib import Path

RESIDUAL_REVIEW = Path(__file__).with_name("residual-review.json")

COMMON = {
    "Carrier Destination": "Destination",
    "CarrierDestination": "Destination",
    "Updated At": "State.Updated At",
    "UpdatedAt": "State.UpdatedAt",
    "Ref ID": "Identity.Ref ID",
    "RefID": "Identity.RefID",
    "Container": "Context.Container",
    "Topics": "Context.Topics",
    "Subjects.Active": "Context.Topics.Main Subject",
    "Subjects.Passive": "Context.Topics.Dependencies",
    "Subjects": "Context.Topics",
    "Status": "State.Status",
    "Version": "State.Version",
    "Label": "Context.Label",
    "Tier": "Context.Tier",
    "Role": "Context.Role",
    "Form": "Context.Form",
    "ID": "Identity.ID",
}
ROLE_FIELDS = {
    "Concern": {"Priority"},
    "Plan": {
        "Work Sequence Number",
        "WorkSequenceNumber",
        "AI Agent Confidence Threshold",
        "AIAgentConfidenceThreshold",
    },
}
ALL_FIELDS = tuple(sorted((*COMMON, *(x for v in ROLE_FIELDS.values() for x in v)), key=len, reverse=True))
FIELD = "|".join(re.escape(x) for x in ALL_FIELDS)
BARE_COMMON_FIELDS = tuple(field for field in COMMON if not field.startswith("Subjects"))
BARE_COMMON_FIELD = "|".join(re.escape(x) for x in sorted(BARE_COMMON_FIELDS, key=len, reverse=True))
SPECIAL_FIELD = "|".join(
    re.escape(x) for x in sorted((x for v in ROLE_FIELDS.values() for x in v), key=len, reverse=True)
)
DIRECT_ATOM = re.compile(rf"(?<![A-Za-z0-9_$.])Atom\.Header\.(?P<field>{FIELD})\b")
DIRECT_VAR = re.compile(rf"(?P<var>\$[A-Za-z_][A-Za-z0-9_]*)\.Header\.(?P<field>{FIELD})\b")
DIRECT_ROLE = re.compile(rf"(?P<role>Concern|Plan)\.Header\.(?P<field>{SPECIAL_FIELD})\b")
RELATIVE = re.compile(rf"(?<![A-Za-z0-9_$.])\.Header\.(?P<field>{FIELD})\b")
ROLE_QUALIFIED = re.compile(rf"(?P<role>Concern|Plan)/\(\.Header\.(?P<field>{SPECIAL_FIELD})\b")
ATOM_CONTEXT = re.compile(r"(?<![A-Za-z0-9_])Atom/(?:/|\()|<Atom>")
ATOM_ROLE = re.compile(
    r"Atom/(?:/)?\(\.Header(?:\.Context)?\.Role\s*(?::=|:|=)\s*(?P<role>Concern|Plan)\s*\)"
)
ATOM_BINDING = re.compile(
    r"(?P<root>Atom|Concern|Plan)(?:/\(\.Header(?:\.Context)?\.Role\s*(?::=|:|=)\s*(?P<role>Concern|Plan)\s*\))?//(?P<var>\$[A-Za-z_][A-Za-z0-9_]*)"
)
TYPED_ATOM = re.compile(r"(?P<var>\$[A-Za-z_][A-Za-z0-9_]*)\s*\[\s*<Atom>\s*\]")
SUMMARY = re.compile(r"(?m)^## Summary\s*$")
E240_BARE = re.compile(r"(?<![A-Za-z0-9_.])Header\.(?P<field>Subjects\.Active)\b")
BARE_COMMON = re.compile(rf"(?<![A-Za-z0-9_$.])Header\.(?P<field>{BARE_COMMON_FIELD})\b")
BARE_COMMON_PATHS = frozenset(row[0] for row in json.loads(RESIDUAL_REVIEW.read_text()))
E240_PATHS = frozenset(
    {
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/CA-E-240-CORE_META_MODEL-EVAL_CASE--validate-atom-scope-and-claim-scope.md",
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/draft/CA-E-240@50-draft-CORE_META_MODEL-EVAL_CASE--validate-atom-scope-and-claim-scope.md",
    }
)
