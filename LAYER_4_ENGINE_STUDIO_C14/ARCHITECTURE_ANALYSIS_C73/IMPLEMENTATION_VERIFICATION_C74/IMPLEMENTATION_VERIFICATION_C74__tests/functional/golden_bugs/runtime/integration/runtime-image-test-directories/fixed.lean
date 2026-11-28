import Lean
def transientdirectories : List String := [".git", ".mypy_cache", ".nox", ".pytest_cache", ".ruff_cache", ".testcache", ".tox", ".venv", ".virtualenv", "__pycache__", "node_modules", "testcache", "tmp", "venv", "virtualenv"]
def credentialdirectories : List String := [".credentials", ".secrets", ".vault", "credentials", "secrets", "vault"]
def excluded (name : String) : Bool := (transientdirectories.contains name || credentialdirectories.contains name || name.startsWith ".anechoic_" || name.endsWith "__tests")
#eval IO.println (Lean.toJson (["FEATURE_MCP__tests", "FEATURE_MCP__tests_old", "FEATURE_MCP", ".git", "credentials", ".anechoic_tmp"].map excluded)).compress
