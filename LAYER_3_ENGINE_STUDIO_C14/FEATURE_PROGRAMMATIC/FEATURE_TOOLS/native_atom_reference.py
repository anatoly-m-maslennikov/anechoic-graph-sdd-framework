"""Derive a native exact revision reference from Atom identity and State."""


def derive_atom_ref(atom_id: str, version: int, status: str) -> str:
    suffix = "-draft" if status.casefold() == "draft" else ""
    return f"{atom_id}@{version}{suffix}"
