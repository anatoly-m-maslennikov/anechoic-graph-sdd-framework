"""Read the Python Formal Claim section from authored Markdown."""

from markdown_it import MarkdownIt


def iter_formal_claims(body):
    headings = []
    for index, token in enumerate(
        tokens := MarkdownIt("commonmark").parse(body)
    ):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [item for item in headings if item[0] < level]
            headings.append(
                (level, tokens[index + 1].content.casefold().strip())
            )
        elif (
            token.type == "fence"
            and token.info.strip().casefold() == "python"
            and tuple(x[1] for x in headings) == ("claim", "formal claim")
        ):
            yield token.content


def formal_claim(body, *, required=True):
    found = list(iter_formal_claims(body))
    if not found and not required:
        return None
    if len(found) != 1:
        raise ValueError("Expected one Python Formal Claim")
    return found[0]
