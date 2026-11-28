"""Publish a Ticket move and restore its source on a definite failure."""

from .. import effects
from ..common import result
from .tickets.directory_effect import _read_tree
from ..sources.source__shared import bind_query_reader


def _publish_ticket(
    selection,
    path,
    destination,
    digest,
    candidate,
    tree,
    companion,
    target_companion,
    recorded,
    recorded_errors,
    check,
    source_intact,
    rollback,
    move_directory_fn,
):
    with bind_query_reader(None):
        created = effects.create(selection.root, destination, candidate)
        recorded.extend(created.effects)
        if created.errors:
            return result(effects=recorded, errors=created.errors)
        if not check():
            rollback()
            return result(effects=recorded, errors=recorded_errors)
        companion_move = (companion, target_companion, tree)
        failure = _move_companion(
            selection.root,
            companion_move,
            (recorded, recorded_errors),
            check,
            rollback,
            move_directory_fn,
        )
        if failure is not None:
            return failure
        _remove_published_source(
            selection.root,
            path,
            digest,
            companion_move,
            (recorded, recorded_errors),
            source_intact,
            rollback,
            move_directory_fn,
        )


def _remove_published_source(
    root,
    path,
    digest,
    companion_move,
    records,
    source_intact,
    rollback,
    move,
):
    removed = effects.remove(root, path, digest)
    recorded, errors = records
    recorded.extend(removed.effects)
    errors.extend(removed.errors)
    if _definite_failure(removed):
        source, target, tree = companion_move
        if tree is not None and source_intact():
            _restore_companion(
                root, target, source, recorded, errors, rollback, move
            )
        else:
            rollback()


def _definite_failure(outcome):
    return (
        outcome.errors
        and not outcome.effects
        and not any(
            error.get("code") == "effect_uncertain" for error in outcome.errors
        )
    )


def _restore_companion(root, target, source, recorded, errors, rollback, move):
    restored = move(root, target, source)
    recorded.extend(restored.effects)
    errors.extend(restored.errors)
    if not restored.errors:
        rollback()


def _require_current_companion(root, path, tree, recorded, rollback):
    try:
        if _read_tree(root, path) == tree:
            return None
    except OSError, RuntimeError, ValueError:
        pass
    rollback()
    return result(
        effects=recorded,
        errors=[
            {
                "code": "source_changed",
                "message": "Ticket companion changed before publication.",
            }
        ],
    )


def _move_companion(
    root,
    companion_move,
    records,
    check,
    rollback,
    move_directory_fn,
):
    companion, target_companion, tree = companion_move
    recorded, recorded_errors = records
    if tree is None:
        return None
    failure = _require_current_companion(
        root, companion, tree, recorded, rollback
    )
    if failure is not None:
        return failure
    moved = move_directory_fn(root, companion, target_companion)
    recorded.extend(moved.effects)
    recorded_errors.extend(moved.errors)
    if moved.errors:
        if _definite_failure(moved):
            try:
                if _read_tree(root, companion) == tree:
                    rollback()
            except OSError, RuntimeError, ValueError:
                pass
        return result(effects=recorded, errors=recorded_errors)
    if not check():
        _restore_companion(
            root,
            target_companion,
            companion,
            recorded,
            recorded_errors,
            rollback,
            move_directory_fn,
        )
        return result(effects=recorded, errors=recorded_errors)
    return None
