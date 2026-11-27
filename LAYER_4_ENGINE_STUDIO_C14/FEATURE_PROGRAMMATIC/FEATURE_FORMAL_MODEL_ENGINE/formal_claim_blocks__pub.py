"""Compile Python Formal Claim fences into model statements."""

from __future__ import annotations

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import formal_claim_fences  # fmt: skip


def formal_claim_blocks(
    body: str, *, model_class_bindings=None, skip_typed_model_properties=False
) -> tuple[str, ...]:
    """Read model fences at Claim/Formal Claim in the compiler's statement format."""
    blocks: list[str] = []
    for language, text in formal_claim_fences(body):
        if language != "python":
            continue
        from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
            legacy_claim_compiler__pub \
            import compile_python_model_claim  # fmt: skip

        if skip_typed_model_properties:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
                ADAPTERS_C30__shared \
                import parse_native_model_claim  # fmt: skip

            declaration = parse_native_model_claim(text)
            if (
                declaration
                and declaration.get("model_value_format")
                and declaration.get("arguments", {}).get("relation_name")
                == "IS_PROPERTY_OF"
            ):
                continue
        blocks.append(
            ";\n".join(
                compile_python_model_claim(
                    text, model_class_bindings=model_class_bindings
                )
            )
        )
    return tuple(blocks)
