import importlib
import unittest

base = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests.declarations."
)
cases0 = importlib.import_module(base + "_declaration_cases_0")
cases1 = importlib.import_module(base + "_declaration_cases_1")
cases2 = importlib.import_module(base + "_declaration_cases_2")


class ModelDeclarationSourceTests(
    cases0.DeclarationCases0,
    cases1.DeclarationCases1,
    cases2.DeclarationCases2,
    unittest.TestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
