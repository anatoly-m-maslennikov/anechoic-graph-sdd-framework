"""Format Model ingestion diagnostics."""

from uuid import uuid4


def _diagnose(inputs, diagnostics, fallback, error):
    attempt = uuid4().hex
    for issue in inputs.issues if inputs.issues and fallback is None else [{}]:
        diagnostics.append(
            {
                "attempt_id": attempt,
                "accepted_generation": None,
                "severity": "ERROR",
                "code": issue.get("code")
                or getattr(error, "code", "invalid_model_source"),
                "message": issue.get("message") or str(error),
                "atom_ref": issue.get("atom_ref")
                or getattr(error, "atom_ref", None),
                "source_path": issue.get("relative_path")
                or getattr(error, "source_path", None),
                "subject": getattr(error, "subject", None),
            }
        )
