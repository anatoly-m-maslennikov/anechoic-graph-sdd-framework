"""Fixtures for Code Access boundary checks."""

from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CodeAccessOwnership,
)


def _fixture_0_entries():
    return {
        "root": {
            "id": "root",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": {},
        }
    }


def _fixture_1_entries(code):
    return {
        "C46": {
            "id": "C46",
            "parent": None,
            "path": "app",
            "kind": "component",
            "fields": {"boundaries": {"code": code}},
        },
        "app/src/lib": {
            "id": "app/src/lib",
            "parent": "C46",
            "path": "app/src/lib",
            "kind": "package",
            "fields": {},
        },
        "app/tests": {
            "id": "app/tests",
            "parent": "C46",
            "path": "app/tests",
            "kind": "package",
            "fields": {},
        },
    }


def _fixture_2_ownership(code):
    return CodeAccessOwnership(
        {
            "C46": {
                "id": "C46",
                "parent": None,
                "path": "app",
                "kind": "component",
                "fields": {"boundaries": {"code": code}},
            },
            "app/src/lib": {
                "id": "app/src/lib",
                "parent": "C46",
                "path": "app/src/lib",
                "kind": "package",
                "fields": {},
            },
            "app/tests": {
                "id": "app/tests",
                "parent": "C46",
                "path": "app/tests",
                "kind": "package",
                "fields": {},
            },
        },
        {
            "app": "C46",
            "app/src/lib": "app/src/lib",
            "app/tests": "app/tests",
        },
    )


def _fixture_3_entries():
    return {
        "root": {
            "id": "root",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": {},
        },
        "caller": {
            "id": "caller",
            "parent": "root",
            "path": "caller",
            "kind": "package",
            "fields": {},
        },
        "provider": {
            "id": "provider",
            "parent": "root",
            "path": "billing",
            "kind": "package",
            "fields": {},
        },
        "other": {
            "id": "other",
            "parent": "caller",
            "path": "caller/other",
            "kind": "package",
            "fields": {},
        },
    }


def _fixture_4_entries():
    return {
        "root": {
            "id": "root",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": {},
        },
        "provider": {
            "id": "provider",
            "parent": "root",
            "path": "billing",
            "kind": "package",
            "fields": {},
        },
        "child": {
            "id": "child",
            "parent": "provider",
            "path": "billing/child",
            "kind": "package",
            "fields": {},
        },
        "sibling": {
            "id": "sibling",
            "parent": "root",
            "path": "sales",
            "kind": "package",
            "fields": {},
        },
        "descendant": {
            "id": "descendant",
            "parent": "sibling",
            "path": "sales/sub",
            "kind": "package",
            "fields": {},
        },
        "other": {
            "id": "other",
            "parent": "child",
            "path": "billing/child/other",
            "kind": "package",
            "fields": {},
        },
    }


def _fixture_5_entries():
    return {
        "root": {
            "id": "root",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": {"boundaries": {"code": {"imports": {"only": []}}}},
        },
        "a": {
            "id": "a",
            "parent": "root",
            "path": "a",
            "kind": "package",
            "fields": {},
        },
        "b": {
            "id": "b",
            "parent": "root",
            "path": "b",
            "kind": "package",
            "fields": {},
        },
    }


def _fixture_6_entries():
    return {
        "root": {
            "id": "root",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": {},
        },
        "a": {
            "id": "a",
            "parent": "root",
            "path": "a",
            "kind": "component",
            "fields": {"layer": 1},
        },
        "b": {
            "id": "b",
            "parent": "root",
            "path": "b",
            "kind": "component",
            "fields": {"layer": 2},
        },
        "pkg": {
            "id": "pkg",
            "parent": "b",
            "path": "b/p",
            "kind": "package",
            "fields": {},
        },
    }


def _fixture_7_entries():
    return {
        "root": {
            "id": "root",
            "parent": None,
            "path": ".",
            "kind": "component",
            "fields": {},
        },
        "a": {
            "id": "a",
            "parent": "root",
            "path": "a",
            "kind": "component",
            "fields": {"layer": 2},
        },
        "b": {
            "id": "b",
            "parent": "root",
            "path": "b",
            "kind": "component",
            "fields": {"layer": 1},
        },
        "a1": {
            "id": "a1",
            "parent": "a",
            "path": "a/sub",
            "kind": "component",
            "fields": {"layer": 1},
        },
        "b1": {
            "id": "b1",
            "parent": "b",
            "path": "b/sub",
            "kind": "component",
            "fields": {"layer": 9},
        },
        "pkg": {
            "id": "pkg",
            "parent": "b1",
            "path": "b/sub/p",
            "kind": "package",
            "fields": {},
        },
    }
