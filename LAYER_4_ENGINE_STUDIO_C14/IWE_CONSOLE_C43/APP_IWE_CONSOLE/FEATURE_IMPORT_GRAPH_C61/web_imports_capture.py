def read_web_items(root, sources, web, source_class):
    items = []
    for path, source in sources.items():
        if source.language not in web or source.status != "unsupported":
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except OSError as error:
            sources[path] = source_class(
                source.language,
                "read_error",
                source.signature,
                error_message=str(error),
            )
            continue
        except UnicodeError as error:
            sources[path] = source_class(
                source.language,
                "parse_error",
                source.signature,
                error_message=str(error),
            )
            continue
        items.append({"path": path, "text": text, "language": source.language})
    return items


def apply_web_rows(sources, items, rows, import_site_class, source_class):
    for item in items:
        path = item["path"]
        source = sources[path]
        row = rows.get(path, {})
        status = row.get("status")
        if status not in {"parsed", "parse_error"}:
            continue
        sites = tuple(
            import_site_class(
                site["module"],
                site.get("anchor"),
                site["level"],
                site["line"],
                site["column"],
                site["type_only"],
            )
            for site in row.get("sites", ())
        )
        sources[path] = source_class(
            source.language,
            status,
            source.signature,
            sites,
            row.get("error"),
            tuple(map(tuple, row.get("forwarded", ()))),
            tuple(map(tuple, row.get("named_uses", ()))),
        )
