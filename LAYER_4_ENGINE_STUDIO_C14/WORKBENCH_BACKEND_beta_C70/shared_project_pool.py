"""Bounded pool of warm, Project-bound peer processes."""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from threading import Event

from . import shared_host_process


@dataclass
class _Entry:
    selection: object
    identity: tuple
    context: object
    peers: object
    users: int = 0
    touched: int = 0


def _identity(selection):
    try:
        stat = selection.root.stat()
    except OSError:
        raise ValueError('project_declarations_stale') from None
    return stat.st_dev, stat.st_ino


def _start(selection, stop):
    context = shared_host_process.open_peers(selection, stop)
    peers = context.__enter__()
    return context, peers


def _stop(entry):
    entry.context.__exit__(None, None, None)


async def _finish(task, stop=None):
    """Do not abandon a thread that owns peer processes on cancellation."""
    cancelled = None
    while True:
        try:
            result = await asyncio.shield(task)
            break
        except asyncio.CancelledError as error:
            if task.cancelled():
                raise
            cancelled = error
            if stop is not None:
                stop.set()
        except Exception:
            if cancelled is not None:
                raise cancelled
            raise
    if cancelled is not None:
        raise cancelled
    return result


class SharedProjectPool:
    def __init__(self, maximum):
        if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
            raise ValueError('maximum must be a positive integer')
        self.max_loaded_projects = maximum
        self._entries = {}
        self._pending = {}
        self._lock = asyncio.Lock()
        self._closed = False
        self._clock = 0

    def _touch(self, entry):
        self._clock += 1
        entry.touched = self._clock

    async def _reserve(self, selection, key, identity):
        evicted = None
        async with self._lock:
            if self._closed:
                raise ValueError('project_gateway_busy')
            entry = self._entries.get(key)
            if entry is not None:
                stale = entry.selection != selection or entry.identity != identity
                if stale or not entry.peers.alive:
                    if entry.users:
                        raise ValueError('project_declarations_stale' if stale else 'project_gateway_busy')
                    evicted = self._entries.pop(key)
                else:
                    entry.users += 1
                    self._touch(entry)
                    return entry, None
            if key in self._pending:
                raise ValueError('project_gateway_busy')
            if evicted is None and len(self._entries) + len(self._pending) >= self.max_loaded_projects:
                idle = [(k, e) for k, e in self._entries.items() if not e.users]
                if not idle:
                    raise ValueError('project_gateway_busy')
                victim, evicted = min(idle, key=lambda item: item[1].touched)
                del self._entries[victim]
            self._pending[key] = asyncio.current_task()
        return None, evicted

    async def _acquire(self, selection):
        key = str(selection.root)
        identity = _identity(selection)
        entry, evicted = await self._reserve(selection, key, identity)
        if entry is not None:
            return entry

        entry = None
        startup = None
        try:
            if evicted is not None:
                await _finish(asyncio.create_task(asyncio.to_thread(_stop, evicted)))
            stop = Event()
            startup = asyncio.create_task(asyncio.to_thread(_start, selection, stop))
            try:
                context, peers = await _finish(startup, stop)
            except asyncio.CancelledError:
                if not startup.cancelled() and startup.exception() is None:
                    context, _ = startup.result()
                    await _finish(asyncio.create_task(asyncio.to_thread(context.__exit__, None, None, None)))
                raise
            entry = _Entry(selection, identity, context, peers, users=1)
            async with self._lock:
                if self._closed:
                    raise ValueError('project_gateway_busy')
                if _identity(selection) != identity:
                    raise ValueError('project_declarations_stale')
                self._touch(entry)
                self._entries[key] = entry
                entry = None
                return self._entries[key]
        finally:
            try:
                if entry is not None:
                    await _finish(asyncio.create_task(asyncio.to_thread(_stop, entry)))
            finally:
                async with self._lock:
                    self._pending.pop(key, None)

    async def _warm_entry(self, selection):
        identity = _identity(selection)
        async with self._lock:
            entry = self._entries.get(str(selection.root))
            if (self._closed or entry is None or entry.selection != selection
                    or entry.identity != identity or not entry.peers.alive):
                return None
            entry.users += 1
            return entry

    @asynccontextmanager
    async def lease(self, selection, *, start=True):
        entry = await self._acquire(selection) if start else await self._warm_entry(selection)
        if entry is None:
            yield None
            return
        try:
            yield entry.peers
        finally:
            async with self._lock:
                entry.users -= 1
                if start:
                    self._touch(entry)

    def status(self):
        return {'loaded_project_count': len(self._entries),
                'max_loaded_projects': self.max_loaded_projects,
                'loaded_project_processes': [
                    {'instance_id': e.selection.instance_id, 'kernel_pid': e.peers.kernel_pid,
                     'orchestrator_pid': e.peers.orchestrator_pid}
                    for e in self._entries.values()]}

    async def close(self):
        async with self._lock:
            if self._closed:
                return
            self._closed = True
            entries, self._entries = list(self._entries.values()), {}
            pending = [task for task in self._pending.values() if task is not asyncio.current_task()]
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        tasks = [asyncio.create_task(asyncio.to_thread(_stop, entry)) for entry in entries]
        if tasks:
            await _finish(asyncio.gather(*tasks, return_exceptions=True))
