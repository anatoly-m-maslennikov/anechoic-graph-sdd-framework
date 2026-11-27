"""Subject audit source fixture."""


def carrier(
    atom_id, active, passive=(), *, role="Requirement", form="Declaration"
):
    return {
        "source": {
            "atom_id": atom_id,
            "version": 1,
            "path": f"sources/{atom_id}.md",
        },
        "subjects": {"active": active, "passive": list(passive)},
        "body": "## Claim\n",
        "read_view": {"content_role": role, "type": form},
    }
