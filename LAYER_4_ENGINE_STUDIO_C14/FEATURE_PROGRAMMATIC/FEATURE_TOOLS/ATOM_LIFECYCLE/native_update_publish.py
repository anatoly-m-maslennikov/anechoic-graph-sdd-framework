"""Publish a Ticket move and restore its source on a definite failure."""
from . import effects
from .common import result
from .directory_effect import _read_tree
from .source import bind_query_reader


def _publish_ticket(selection, path, destination, digest, candidate, tree,
                    companion, target_companion, recorded, recorded_errors,
                    check, source_intact, rollback, move_directory_fn):
    with bind_query_reader(None):
        created = effects.create(selection.root, destination, candidate)
        recorded.extend(created.effects)
        if created.errors:
            return result(effects=recorded, errors=created.errors)
        if not check():
            rollback()
            return result(effects=recorded, errors=recorded_errors)
        if tree is not None:
            failure = _move_companion(
                selection,
                companion,
                target_companion,
                tree,
                recorded,
                recorded_errors,
                check,
                rollback,
                move_directory_fn,
            )
            if failure is not None:
                return failure
        removed = effects.remove(selection.root, path, digest)
        recorded.extend(removed.effects)
        recorded_errors.extend(removed.errors)
        if (
            removed.errors and not removed.effects
            and not any(
                error.get("code") == "effect_uncertain"
                for error in removed.errors
            )
        ):
            if tree is not None and source_intact():
                restored = move_directory_fn(
                    selection.root, target_companion, companion
                )
                recorded.extend(restored.effects)
                recorded_errors.extend(restored.errors)
                if not restored.errors:
                    rollback()
            else:
                rollback()


def _move_companion(selection, companion, target_companion, tree, recorded,
                    recorded_errors, check, rollback, move_directory_fn):
    if tree is not None:
        try:
            if _read_tree(selection.root, companion) != tree:
                raise ValueError(
                    "Ticket companion changed before publication."
                )
        except OSError, RuntimeError, ValueError:
            rollback()
            return result(
                effects=recorded,
                errors=[
                    {
                        "code": "source_changed",
                        "message": (
                            "Ticket companion changed before publication."
                        ),
                    }
                ],
            )
        moved = move_directory_fn(selection.root, companion, target_companion)
        recorded.extend(moved.effects)
        recorded_errors.extend(moved.errors)
        if moved.errors:
            if not moved.effects and not any(
                error.get("code") == "effect_uncertain"
                for error in moved.errors
            ):
                try:
                    if _read_tree(selection.root, companion) == tree:
                        rollback()
                except OSError, RuntimeError, ValueError:
                    pass
            return result(effects=recorded, errors=recorded_errors)
        if not check():
            restored = move_directory_fn(
                selection.root, target_companion, companion
            )
            recorded.extend(restored.effects)
            recorded_errors.extend(restored.errors)
            if not restored.errors:
                rollback()
            return result(effects=recorded, errors=recorded_errors)
    return None
