import posixpath


def local_value(
    root,
    spec,
    site,
    file,
    dependency_file,
    frontend,
    frontend_path,
):
    if spec.startswith("/"):
        frontend = (
            frontend.relative_to(root)
            if frontend.is_relative_to(root)
            else frontend_path
        )
        if not site.level or not file.is_relative_to(frontend):
            return None
        value = posixpath.normpath(
            posixpath.join(frontend.as_posix(), spec.lstrip("/"))
        )
    else:
        value = posixpath.normpath(
            posixpath.join(dependency_file.parent.as_posix(), spec)
        )
    return None if value == ".." or value.startswith("../") else value


def local_result(
    root, value, sources, written, extensions, web, probe, include_asset_target
):
    candidates = [value + ext for ext in extensions]
    candidates += [
        posixpath.join(value, "index" + ext) for ext in extensions[1:]
    ]
    matches = [
        item
        for item in candidates
        if item in sources and sources[item].language in web
    ]
    if len(matches) == 1:
        return written, "module:" + matches[0], "internal"
    if matches:
        return written, None, "ambiguous"
    asset = root / value
    if asset.suffix.lower() in {".css", ".json"}:
        if probe is not None:
            probe(asset)
        if asset.is_file() and not asset.is_symlink():
            target = "asset:" + value if include_asset_target else None
            return written, target, "asset"
    return written, None, "unresolved"
