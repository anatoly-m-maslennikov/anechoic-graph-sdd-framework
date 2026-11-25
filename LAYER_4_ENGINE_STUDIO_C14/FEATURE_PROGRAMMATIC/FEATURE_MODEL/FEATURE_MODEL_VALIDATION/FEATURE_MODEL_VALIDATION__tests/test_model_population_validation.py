"""Check project-wide uniqueness for nested Model Properties."""

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import unittest

from ..FEATURE_MODEL_VALIDATION__shared import validate_population_uniqueness


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Identity:
    id: str | None


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class State:
    version: int | None
    status: str


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Header:
    identity: Identity
    state: State


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Atom:
    header: Header


RULES = ({"keys": ("Header.Identity.ID", "Header.State.Version")},)


def atom(identifier, version, status):
    return Atom(Header(Identity(identifier), State(version, status)))


class ModelPopulationValidationTests(unittest.TestCase):
    def test_unique_pair_across_all_statuses(self):
        proposed = atom("CA-R-1", 2, "Draft")
        peers = [atom("CA-R-1", 1, "Active"), atom("CA-R-2", 2, "Archived")]
        validate_population_uniqueness(Atom, proposed, peers, RULES)
        for status in ("Draft", "Active", "Archived", "Backlog"):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "uniqueness violated"):
                validate_population_uniqueness(Atom, proposed, [atom("CA-R-1", 2, status)], RULES)

    def test_invalid_population_or_missing_property_fails(self):
        proposed = atom("CA-R-1", 2, "Draft")
        with self.assertRaisesRegex(ValueError, "other instances"):
            validate_population_uniqueness(Atom, proposed, [proposed], RULES)
        with self.assertRaisesRegex(ValueError, "unavailable"):
            validate_population_uniqueness(Atom, proposed, [], ({"keys": ("Header.ID",)},))
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            validate_population_uniqueness(Atom, proposed, [], ({"keys": ("Header.Identity.ID",), "status": "Active"},))
        with self.assertRaisesRegex(ValueError, "expected one"):
            validate_population_uniqueness(Atom, atom(None, 2, "Draft"), [], RULES)

    def test_active_rule_checks_only_instances_with_the_declared_values(self):
        keys = ("Header.Identity.ID", "Header.State.Version")
        rules = ({"keys": keys, "status": "Active", "single_value_paths": keys},)
        proposed = atom("CA-R-1", 2, "active")
        validate_population_uniqueness(
            Atom, proposed, [atom("CA-R-1", 2, "Done"), atom("CA-R-1", None, "Active")], rules,
        )
        with self.assertRaisesRegex(ValueError, "uniqueness violated"):
            validate_population_uniqueness(Atom, proposed, [atom("CA-R-1", 2, "Active")], rules)

    def test_derived_ref_id_is_unique_across_peers(self):
        @dataclass(config=ConfigDict(strict=True, extra="forbid"))
        class StrictAtom:
            atom_id: str
            version: int

            @property
            def ref_id(self):
                return f"{self.atom_id}@{self.version}"

        rules = ({"keys": ("Ref ID",)},)
        proposed = StrictAtom("AN-S-1", 1)
        validate_population_uniqueness(StrictAtom, proposed, [StrictAtom("AN-S-1", 2)], rules)
        with self.assertRaisesRegex(ValueError, "uniqueness violated"):
            validate_population_uniqueness(StrictAtom, proposed, [StrictAtom("AN-S-1", 1)], rules)


if __name__ == "__main__":
    unittest.main()
