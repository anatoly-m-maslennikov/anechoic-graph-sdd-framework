"""Packaged Atom Dependencies check for the reviewed R2708 Python Claim."""

from hashlib import sha256
from inspect import getsource

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.topic_dependencies__pub \
    import DEPENDENCIES_CHECK_SOURCE_SHA256  # fmt: skip


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
class Atom:
    dependencies: tuple[str, ...]


def dependencies_are_distinct(atom: Atom) -> bool:
    return len(atom.dependencies) == len(set(atom.dependencies))


DEPENDENCIES_CLAIM_SHA256 = (
    "86d99456998790f8b479ab1fa958721780d47d5a8b605853270c458a9d4b6759"
)


def verify_packaged_dependencies_check():
    if (
        sha256(
            getsource(dependencies_are_distinct).rstrip("\n").encode()
        ).hexdigest()
        != DEPENDENCIES_CHECK_SOURCE_SHA256
    ):
        raise ValueError(
            "Packaged Atom Dependencies check differs from the reviewed Claim"
        )
