"""Tests for Python model declarations and record review."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import (
    static_checks,
)

python_model_findings = (
    static_checks.source_languages.source_python_models.python_model_findings
)


class PythonModelFindingsTests(unittest.TestCase):
    def test_import_aliases_and_declaration_forms(self):
        source = """import dataclasses as dc
from dataclasses import dataclass as model
import typing as t
from typing_extensions import TypedDict as TD, NamedTuple as NT
from collections import namedtuple as tuple_factory
@dc.dataclass
class First: pass
@model(frozen=True)
class Second: pass
class Third(t.TypedDict): pass
class Fourth(NT): pass
Fifth = TD("Fifth", {"value": int})
Sixth = tuple_factory("Sixth", "value")
Seventh = dc.make_dataclass("Seventh", [])
Eighth = dc.dataclass(Existing)
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:6: dataclasses.dataclass",
                "sample.py:8: dataclasses.dataclass",
                "sample.py:10: typing.TypedDict",
                "sample.py:11: typing_extensions.NamedTuple",
                "sample.py:12: typing_extensions.TypedDict",
                "sample.py:13: collections.namedtuple",
                "sample.py:14: dataclasses.make_dataclass",
                "sample.py:15: dataclasses.dataclass",
            ],
        )

    def test_pydantic_and_ordinary_classes_are_allowed(self):
        source = """from pydantic import BaseModel
from pydantic.dataclasses import dataclass
import pydantic.dataclasses as pd
@dataclass
class First: pass
@pd.dataclass(frozen=True)
class Second: pass
class Third(BaseModel): pass
class Fourth: pass
value = {"name": "test"}
"""
        self.assertEqual(python_model_findings("sample.py", source), [])

    def test_shadowed_alias_is_not_reported(self):
        source = """from typing import NamedTuple as model
first = model("First", [])
model = custom
second = model("Second", [])
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:2: typing.NamedTuple",
            ],
        )

    def test_plain_record_classes_and_ordinary_classes(self):
        source = """from typing import ClassVar
class FieldRecord:
    name: str
class ConstructorRecord(object):
    def __init__(self, name):
        self.name = name
class Constants:
    VERSION: ClassVar[int] = 1
class Service:
    def __init__(self, name):
        self.name = name
    def start(self):
        return self.name
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:2: plain class record",
                "sample.py:4: plain class record",
            ],
        )

    def test_namespace_records_resolve_aliases_and_flag_known_fields(self):
        source = """from types import SimpleNamespace as Namespace
import types as t
first = Namespace(id=1, title="A")
second = t.SimpleNamespace({"id": 1, "title": "A"})
third = Namespace(**{"id": 1, "title": "A"})
adapter = Namespace(call=reader, close=closer)  # pragma: anechoic-model-adapter - interface adapter
single = Namespace(id=1)
Namespace = factory
custom = Namespace(id=1, title="A")
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:3: types.SimpleNamespace record",
                "sample.py:4: types.SimpleNamespace record",
                "sample.py:5: types.SimpleNamespace record",
            ],
        )
        self.assertEqual(
            python_model_findings("sample__tests/fixture.py", source),
            [
                "sample__tests/fixture.py:3: types.SimpleNamespace record",
                "sample__tests/fixture.py:4: types.SimpleNamespace record",
                "sample__tests/fixture.py:5: types.SimpleNamespace record",
            ],
        )

    def test_dictionary_records_and_ordinary_maps(self):
        source = """from typing import Any as Value, Dict, Union
first: dict[str, object] = {"id": 1, "title": "A"}
second: Dict[str, Value] = dict(id=1, title="A")
third: dict[str, int | str] = {"id": 1, "title": "A"}
fourth: Dict[str, Union[int, str]] = {"id": 1, "title": "A"}
sources: dict[str, object] = {"src/a.py": "text", "src/b.py": "other"}
names: dict[str, str] = {"first": "A", "second": "B"}
dynamic: dict[str, object] = {name: value for name, value in pairs}
local = {"id": 1, "title": "A"}
use(local["id"], local["title"])
source_map = {"src/a.py": "text", "src/b.py": "other"}
use(source_map["src/a.py"], source_map["src/b.py"])
rebound = {"id": 1, "title": "A"}
rebound = source
use(rebound["id"], rebound["title"])
opts: dict[str, object] = {"a": 1, "b": True}
use(**opts)
payload = {"id": 1, "title": "A"}
json.dumps(payload)
mapping = {"id": 1, "title": "A"}
use(mapping["id"], mapping["title"])
unknown: dict[str, object] = {"id": 1, "name": "A"}
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:2: possible dictionary record",
                "sample.py:3: possible dictionary record",
                "sample.py:4: possible dictionary record",
                "sample.py:5: possible dictionary record",
                "sample.py:9: possible dictionary record",
                "sample.py:16: possible dictionary record",
                "sample.py:20: possible dictionary record",
                "sample.py:22: possible dictionary record",
            ],
        )

    def test_dictionary_candidates_are_advisory_with_blocking_findings(self):
        gate = static_checks.source_languages
        output, errors = StringIO(), StringIO()
        candidate = "sample.py:1: possible dictionary record"
        violation = "sample.py:2: plain class record"
        advisory = "sample.py:3: Pydantic TypeAdapter constructed in a loop"
        with (
            patch.object(gate, "_enabled", return_value=True),
            patch.object(
                gate,
                "source_language_findings",
                side_effect=[[candidate, advisory], [candidate, violation]],
            ),
            redirect_stdout(output),
            redirect_stderr(errors),
        ):
            self.assertEqual(gate.check(Path(".")), 0)
            self.assertEqual(gate.check(Path(".")), 1)
        self.assertIn(candidate, output.getvalue())
        self.assertIn(advisory, output.getvalue())
        self.assertIn("Source language review", output.getvalue())
        self.assertIn(violation, errors.getvalue())
        self.assertNotIn(candidate, errors.getvalue())

    def test_recognizable_untagged_model_unions(self):
        source = """from typing import Annotated, Literal, TypeAlias, Union
from pydantic import BaseModel, Field
class StateModel(BaseModel):
    pass
class Ready(StateModel):
    state: Literal["ready"]
class Pending(StateModel):
    state: Literal["pending"]
Plain = Ready | Pending
Legacy: TypeAlias = Union[Ready, Pending]
type Native = Ready | Pending
Tagged = Annotated[Ready | Pending, Field(discriminator="state")]
class Reply(BaseModel):
    state: Union[Ready, Pending] = Field(discriminator="state")
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:9: Pydantic model union needs a discriminator",
                "sample.py:10: Pydantic model union needs a discriminator",
                "sample.py:11: Pydantic model union needs a discriminator",
            ],
        )

    def test_json_decode_and_repeated_adapter_candidates(self):
        source = """from json import loads
from pydantic import TypeAdapter as Adapter
typed = Model.model_validate(loads(payload))
custom = Model.model_validate(loads(payload, object_pairs_hook=policy))
direct = Model.model_validate_json(payload)
adapter = Adapter(list[Model])
for item in payloads:
    adapter.validate_python(item)
    Adapter(Model).validate_python(item)
    def later():
        return Adapter(Model)
"""
        self.assertEqual(
            python_model_findings("sample.py", source),
            [
                "sample.py:3: Pydantic model_validate after json.loads",
                "sample.py:9: Pydantic TypeAdapter constructed in a loop",
            ],
        )

    def test_parse_failure_is_visible(self):
        with self.assertRaises(SyntaxError) as error:
            python_model_findings("broken.py", "class :")
        self.assertEqual(error.exception.filename, "broken.py")
