from __future__ import annotations

from types import MappingProxyType
from typing import Sequence
import re
from .subject_notation_types import GrammarSource, GrammarPin, SubjectProfile, SubjectNotationError

_LEGACY_PINS = (
    GrammarPin(
        "CA-R-1204",
        14,
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/archive/CA-R-1204-CORE_META_MODEL--use-subject-path-slash-only-for-bearer-qualification@14.md",
        "f57d56dab2cff12ea38a94900a1f146e40ead39f0af9e26e3130e9867f290dda",
    ),
    GrammarPin(
        "CA-R-1321",
        12,
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/archive/CA-R-1321-CORE_META_MODEL-CORE--define-subject-expression@12.md",
        "6baf3f4179591dcc89c458dcb6503a55f24b70f9f1bd93203f4b748a9bcb1b8c",
    ),
    GrammarPin(
        "CA-R-1324",
        10,
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/archive/CA-R-1324-CORE_META_MODEL-REQUIREMENT--reserve-subject-expression-separators@10.md",
        "f38d4cc446b04cde6958f1fe011679ff95048bdfe30f360d11a7366a572bc0b1",
    ),
    GrammarPin(
        "CA-M-228",
        14,
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/archive/CA-M-228-CORE_META_MODEL-METHOD--write-subject-expressions-with-bearer-and-value-qualification@14.md",
        "f5a2152648b95c04af56c49118f43ac64ee46dd8183b23913cb64f335d6f26df",
    ),
    GrammarPin(
        "CA-E-383",
        13,
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/archive/CA-E-383-CORE_META_MODEL-EVALUATION_APPROACH--reject-invalid-subject-expressions@13.md",
        "00c3e901fbd18cdb584387386f6b04cd43905f651c4369e16a97d20b469b3274",
    ),
)

_APPROVED_SOURCES = (
    GrammarSource(
        "CA-R-1931",
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1931-CORE_META_MODEL-RULE--use-subject-path-separators-for-broader-to-narrower-and-bearer-to-dependent.md",
    ),
    GrammarSource(
        "CA-R-1321",
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1321-CORE_META_MODEL-RULE--define-subject-expression.md",
    ),
    GrammarSource(
        "CA-R-1324",
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1324-CORE_META_MODEL-RULE--reserve-subject-expression-separators.md",
    ),
    GrammarSource(
        "CA-M-228",
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/CA-M-228-CORE_META_MODEL-IMPLEMENTATION_METHOD--write-subject-expressions-with-bearer-and-value-qualification.md",
    ),
    GrammarSource(
        "CA-E-833",
        ".anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/06_evaluation/CA-E-833-CORE_META_MODEL-EVAL_POLICY--validate-entity-and-topic-reference-expressions.md",
    ),
)

_PROFILES = MappingProxyType(
    {
        "legacy": SubjectProfile(
            name="legacy",
            separators=("/", ":"),
            bearer_separator="/",
            grammar_pins=_LEGACY_PINS,
        ),
        "approved": SubjectProfile(
            name="approved",
            separators=("//", "/", ".", ":", "+>", "<+", ">|", "|<", "<-->", "<((", "(("),
            bearer_separator=".",
            grammar_pins=_APPROVED_SOURCES,
        ),
    }
)

def get_profile(name: str = "legacy") -> SubjectProfile:
    """Return one immutable named profile; no profile is inferred from text."""

    if not isinstance(name, str) or not name:
        raise SubjectNotationError("profile-invalid", "subject profile must be one non-empty string")
    try:
        return _PROFILES[name]
    except KeyError as error:
        raise SubjectNotationError("profile-unknown", f"unknown subject profile: {name}") from error


def profile_evidence(
    name: str = "legacy", *, grammar_pins: Sequence[GrammarPin] | None = None,
) -> dict[str, object]:
    """Project explicit current observations or the declared legacy history."""

    profile = get_profile(name)
    pins = tuple(grammar_pins) if grammar_pins is not None else profile.grammar_pins
    if any(not isinstance(pin, GrammarPin) for pin in pins):
        raise SubjectNotationError("profile-evidence-unbound", "Current grammar observations are required")
    if len(pins) != len(profile.grammar_pins) or any(
        pin.atom_id != source.atom_id
        or (isinstance(source, GrammarPin) and pin.path != source.path)
        for pin, source in zip(pins, profile.grammar_pins, strict=True)
    ):
        raise SubjectNotationError("profile-evidence-invalid", "Grammar observations must match the selected sources")
    rows = []
    for pin in pins:
        if not isinstance(pin, GrammarPin) or type(pin.version) is not int or pin.version < 1 or not isinstance(pin.sha256, str) or re.fullmatch(r"[0-9a-f]{64}", pin.sha256) is None:
            raise SubjectNotationError("profile-evidence-invalid", "Grammar observations require a Version and SHA-256")
        rows.append({"atom_id": pin.atom_id, "version": pin.version, "path": pin.path, "sha256": pin.sha256})
    return {
        "grammar_pins": rows,
        "native_admission": "not_performed",
    }

