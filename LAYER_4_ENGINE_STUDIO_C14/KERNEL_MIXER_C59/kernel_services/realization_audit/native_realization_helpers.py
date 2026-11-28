"""Prepare realization options and refresh its published metadata."""

from pathlib import Path, PurePosixPath
import keyword
import sys


def import_options(self, workbench: dict):
    config = workbench.get("import_graph", {})
    if config is False:
        return None
    if not isinstance(config, dict):
        raise ValueError(
            "runtime.iwe_console.import_graph must be a mapping or false"
        )
    result = []
    for name, default in (("python_roots", None), ("include", [])):
        values = config.get(name, default)
        if name == "python_roots" and name not in config:
            result.append(None)
            continue
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value for value in values
        ):
            raise ValueError(
                f"import_graph.{name} must be a list of Project-relative paths"
            )
        for value in values:
            path = Path(value)
            if (
                path.is_absolute()
                or ".." in path.parts
                or not (self._root / path)
                .resolve()
                .is_relative_to(self._root.resolve())
            ):
                raise ValueError(
                    f"import_graph.{name} paths must be inside the Project"
                )
            if name == "include" and (
                path == Path(".") or (self._root / path).is_dir()
            ):
                raise ValueError(
                    "import_graph.include paths must name source files"
                )
        result.append(tuple(values))
    validated = self._image_import_options(config)
    return result[0], result[1], validated


def image_import_options(self, config):
    image_imports = config.get("python_image_imports", {})
    if not isinstance(image_imports, dict):
        raise ValueError("import_graph.python_image_imports must be a mapping")
    validated = {}
    for value, modules in image_imports.items():
        if not isinstance(value, str) or not value:
            raise ValueError(
                "import_graph.python_image_imports keys must name Python "
                "source files"
            )
        path = Path(value)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not (self._root / path)
            .resolve()
            .is_relative_to(self._root.resolve())
        ):
            raise ValueError(
                "import_graph.python_image_imports paths must be inside the "
                "Project"
            )
        if (
            path.as_posix() != value
            or path.suffix != ".py"
            or (self._root / path).is_dir()
        ):
            raise ValueError(
                "import_graph.python_image_imports keys must name Python "
                "source files"
            )
        if not _valid_modules(modules):
            raise ValueError(
                "import_graph.python_image_imports values must be lists of "
                "dotted Python module names"
            )
        validated[value] = tuple(modules)
    return validated


def publish_metadata(
    self,
    store,
    capture,
    binding_states,
    atoms_only,
    boundary_tables,
    read_import_sources,
    replace_package_audit,
    replace_component_metrics,
):
    from ...component_metrics import measure_components, refresh_spec_sizes

    connection = store._connection
    if self._realization_options is None:
        connection.execute("DROP TABLE IF EXISTS main.component_metrics")
        connection.execute("DROP TABLE IF EXISTS main.package_audit")
        boundary_tables.remove_boundaries(connection)
        return
    nodes = connection.execute(
        "SELECT node_key, kind, language, relative_path, scan_status, "
        "package_key, package_type FROM main.import_nodes"
    ).fetchall()
    tests = connection.execute(
        "SELECT source_key, target_key FROM main.test_edges"
    ).fetchall()
    replace_package_audit(
        connection, self.selection, capture, nodes, binding_states, tests=tests
    )
    if atoms_only:
        measurements = refresh_spec_sizes(
            connection, capture, self.selection.project_prefix
        )
    else:
        sources = read_import_sources(connection)
        try:
            measurements = measure_components(
                self.selection, capture, sources, nodes, tests
            )
        except (OSError, RuntimeError, ValueError) as error:
            print(f"Component metrics unavailable: {error}", file=sys.stderr)
            measurements = []
    replace_component_metrics(connection, measurements)


def refresh_traces(
    self,
    store,
    paths,
    PACKAGE_SUFFIX,
    SUFFIX,
    native_trace_snapshot,
    replace_package_audit,
):
    owners = _trace_owners(self._root, paths, PACKAGE_SUFFIX, SUFFIX)
    connection = store._connection
    with store._lock, self._transaction(store):
        nodes = []
        for kind, relative in owners:
            nodes.extend(
                connection.execute(
                    "SELECT node_key, kind, language, relative_path, "
                    "scan_status, package_key "
                    "FROM main.import_nodes WHERE kind = ? AND "
                    "relative_path = ?",
                    [kind, relative],
                ).fetchall()
            )
        traces, states = native_trace_snapshot(self._root, nodes)
        for _, kind, _, relative, _, _ in nodes:
            connection.execute(
                "DELETE FROM main.implementation_rmedo WHERE owner_path = ?",
                [relative],
            )
            if kind == "package":
                states.setdefault(relative, "missing")
        if traces:
            connection.executemany(
                "INSERT INTO main.implementation_rmedo VALUES (?, ?, ?, ?, ?)",
                traces,
            )
        if states:
            _refresh_trace_audit(
                self, connection, states, replace_package_audit
            )


def atom_source_paths(self, batch, project_goal_filename):
    control = self.selection.control_relative
    generated = control / "000_ANECHOIC_framework"
    files: set[PurePosixPath] = set()
    for change in batch:
        for key in ("old_path", "new_path"):
            raw_path = change.get(key)
            if raw_path is None:
                continue
            path = PurePosixPath(raw_path)
            if (
                not path.is_relative_to(control)
                and not (
                    len(path.parts) == 1
                    and (
                        path
                        == self.selection.manifest_path.relative_to(self._root)
                        or project_goal_filename(path.name)
                    )
                )
            ) or path.is_relative_to(generated):
                continue
            if (
                path.suffix == ".md"
                or (self._root / path).is_dir()
                or (
                    key == "old_path"
                    and any(
                        raw_path != row["source_path"]
                        and row["source_path"].startswith(raw_path + "/")
                        for row in self._capture.atoms
                    )
                )
            ):
                files.add(path)
    return files


def _trace_owners(root, paths, PACKAGE_SUFFIX, SUFFIX):
    owners = set()
    for relative in paths:
        path = PurePosixPath(relative)
        parent_name = path.parent.name or root.name
        if (
            path.name == parent_name + PACKAGE_SUFFIX
            or path.name == parent_name + ".p" + SUFFIX
        ):
            owners.add(("package", path.parent.as_posix()))
        elif path.name.endswith(SUFFIX) and path.name != SUFFIX:
            owners.add(
                (
                    "module",
                    path.with_name(path.name.removesuffix(SUFFIX)).as_posix(),
                )
            )
    return owners


def _refresh_trace_audit(self, connection, states, replace_package_audit):
    retained = dict(
        connection.execute(
            "SELECT relative_path, binding_status FROM main.package_audit"
        ).fetchall()
    )
    retained.update(states)
    nodes = connection.execute(
        "SELECT node_key, kind, language, relative_path, scan_status, "
        "package_key, package_type "
        "FROM main.import_nodes"
    ).fetchall()
    tests = connection.execute(
        "SELECT source_key, target_key FROM main.test_edges"
    ).fetchall()
    replace_package_audit(
        connection,
        self.selection,
        self._capture,
        nodes,
        retained,
        tests=tests,
    )


def _valid_modules(modules):
    return isinstance(modules, list) and all(
        isinstance(module, str)
        and bool(module)
        and all(
            part.isidentifier() and not keyword.iskeyword(part)
            for part in module.split(".")
        )
        for module in modules
    )
