"""Check Python command arguments and bytecode environment options."""

from pathlib import Path
import re


PYTHON = re.compile(r"^(?:.*/)?python(?:\d+(?:\.\d+)*)?(?:\.exe)?$")
BOUNDARY = re.compile(r"(?:^|/)\.anechoic_tmp(?:/|$)")
ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*=")
SHORT_OPTIONS = re.compile(r"^-[bBdEhiIOPqRsSuvVx]+$")


def safe_prefix(value):
    return bool(BOUNDARY.search(value)) and ".." not in Path(value).parts


def _python_options(args):
    flags, prefix = set(), None
    position = 0
    while position < len(args):
        arg = args[position]
        if arg in {"-m", "-c", "-", "--"} or not arg.startswith("-"):
            break
        if arg in {"-X", "-W"}:
            position += 1
            value = args[position] if position < len(args) else ""
            if arg == "-X" and value.startswith("pycache_prefix="):
                prefix = value.split("=", 1)[1]
        elif arg.startswith("-Xpycache_prefix="):
            prefix = arg.split("=", 1)[1]
        elif SHORT_OPTIONS.fullmatch(arg):
            flags.update(arg[1:])
        elif arg in {
            "--version",
            "--help",
            "--help-env",
            "--help-xoptions",
            "--help-all",
        }:
            flags.add("h")
        position += 1
    return flags, prefix, args[position:]


def _uv_command(command, environment):
    if (
        Path(command[0]).name in {"uv", "uv.exe"}
        and len(command) > 1
        and command[1] in {"run", "sync", "pip"}
    ):
        python_index = next(
            (
                i
                for i, item in enumerate(command[2:], 2)
                if PYTHON.fullmatch(item)
            ),
            len(command),
        )
        compile_option = next(
            (
                item
                for item in reversed(command[:python_index])
                if item in {"--compile-bytecode", "--no-compile-bytecode"}
            ),
            "",
        )
        compile_requested = environment.get("UV_COMPILE_BYTECODE", "") in {
            "1",
            "true",
            "yes",
        }
        if (
            compile_option == "--compile-bytecode"
            or not compile_option
            and compile_requested
        ):
            return None
        command = command[python_index:] if command[1] == "run" else []
    return command


def _command_environment(tokens):
    environment = {}
    for index, token in enumerate(tokens):
        if ASSIGNMENT.match(token):
            key, value = token.split("=", 1)
            environment[key] = value
        elif Path(token).name not in {
            "env",
            "-S",
            "exec",
            "command",
            "if",
            "then",
            "do",
            "CMD",
        }:
            return tokens[index:], environment
    return [], environment


def unsafe(tokens):
    command, environment = _command_environment(tokens)
    if not command:
        return False
    command = _uv_command(command, environment)
    if command is None:
        return True
    if not command or not PYTHON.fullmatch(command[0]):
        return False
    flags, prefix, target = _python_options(command[1:])
    if target[:1] == ["<spread>"] or flags & {"h", "V"}:
        return False
    if not flags & {"E", "I"}:
        prefix = (
            environment.get("PYTHONPYCACHEPREFIX", "")
            if prefix is None
            else prefix
        )
        if environment.get("PYTHONDONTWRITEBYTECODE") and target[:2] not in (
            ["-m", "compileall"],
            ["-m", "py_compile"],
        ):
            return False
    contained = safe_prefix(prefix or "")
    if target[:2] in (["-m", "compileall"], ["-m", "py_compile"]):
        return (
            not contained or target[1] == "compileall" and "-b" in target[2:]
        )
    return "B" not in flags and not contained
