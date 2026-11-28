"""Tests for Python model declarations and record review."""

import unittest

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
        source = (
            """from types import SimpleNamespace as Namespace
import types as t
first = Namespace(id=1, title="A")
second = t.SimpleNamespace({"id": 1, "title": "A"})
third = Namespace(**{"id": 1, "title": "A"})
"""
            "adapter = Namespace(call=reader, close=closer)  # pragma: "
            "anechoic-model-adapter - interface adapter\n"
            """single = Namespace(id=1)
Namespace = factory
custom = Namespace(id=1, title="A")
"""
        )
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
