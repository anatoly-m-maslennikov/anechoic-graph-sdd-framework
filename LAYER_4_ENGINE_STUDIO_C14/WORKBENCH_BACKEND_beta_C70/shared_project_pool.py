"""Bounded pool of warm, Project-bound peer processes."""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import sys
from threading import Event
from time import monotonic

from . import shared_host_process


@dataclass
class _Entry:
    selection: object
    identity: tuple
    context: object
    peers: object
    users: int = 0
    touched: int = 0
    admitted: bool = False
    startup_error: str | None = None
    admission_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    recover_after: float = 0.0

    async def wait_ready(self):
        async with self.admission_lock:
            if self.startup_error is not None:
                raise RuntimeError(self.startup_error)
            if self.admitted:
                return
            try:
                await self.peers.wait_ready(self.selection.instance_id)
            except (RuntimeError, ValueError) as error:
                self.startup_error = str(error)
                raise
            self.admitted = True


def _identity(selection):
    try:
        stat = selection.root.stat()
    except OSError:
        raise ValueError('project_declarations_stale') from None
    return stat.st_dev, stat.st_ino


def _start(selection, stop, warm_worker=None):
    context = shared_host_process.open_peers(selection, stop, warm_worker) if warm_worker else shared_host_process.open_peers(selection, stop)
    peers = context.__enter__()
    return context, peers


def _stop(entry):
    entry.context.__exit__(None, None, None)


async def _finish(task, stop=None):
    """Do not abandon a thread that owns peer processes on cancellation."""
    cancelled = None
    while not task.done():
        try:
            await asyncio.wait((task,))
        except asyncio.CancelledError as error:
            cancelled = error
            if stop is not None:
                stop.set()
    if cancelled is not None:
        if not task.cancelled():
            task.exception()
        raise cancelled
    return task.result()


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
        self.warm_worker = None

    def _touch(self, entry):
        self._clock += 1
        entry.touched = self._clock

    async def _reserve(self, selection, key, identity):
        evicted = None
        async with self._lock:
            if self._closed or key in self._pending:
                raise ValueError('project_gateway_busy')
            entry = self._entries.get(key)
            if entry is not None:
                stale = entry.selection != selection or entry.identity != identity
                if stale or not entry.peers.alive or entry.startup_error is not None:
                    if entry.users or (not stale and monotonic() < entry.recover_after):
                        raise ValueError('project_declarations_stale' if stale else 'project_gateway_busy')
                    evicted = self._entries.pop(key)
                else:
                    entry.users += 1
                    self._touch(entry)
                    return entry, None
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
        return await self._start_reserved(selection, key, identity, evicted)

    async def _start_reserved(self, selection, key, identity, evicted, *, revalidate=None):
        entry = None
        try:
            if evicted is not None:
                await _finish(asyncio.create_task(asyncio.to_thread(_stop, evicted)))
            if revalidate is not None:
                await revalidate(selection)
                if _identity(selection) != identity:
                    raise ValueError('project_declarations_stale')
            entry = await self._start_entry(selection, identity)
            if revalidate is not None:
                await entry.wait_ready()
                await revalidate(selection)
            async with self._lock:
                if self._closed:
                    raise ValueError('project_gateway_busy')
                if _identity(selection) != identity:
                    raise ValueError('project_declarations_stale')
                if revalidate is None:
                    entry.users = 1
                    self._touch(entry)
                else:
                    if not entry.peers.alive:
                        raise RuntimeError('Beta peers exited during recovery')
                    entry.touched, entry.recover_after = evicted.touched, monotonic() + 2
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

    async def _start_entry(self, selection, identity):
        stop = Event()
        args = (selection, stop, self.warm_worker) if self.warm_worker else (selection, stop)
        startup = asyncio.create_task(asyncio.to_thread(_start, *args))
        try:
            context, peers = await _finish(startup, stop)
        except asyncio.CancelledError:
            if not startup.cancelled() and startup.exception() is None:
                context, _ = startup.result()
                await _finish(asyncio.create_task(asyncio.to_thread(context.__exit__, None, None, None)))
            raise
        return _Entry(selection, identity, context, peers)

    def _can_recover(self, entry):
        return (entry.admitted and not entry.users and monotonic() >= entry.recover_after
                and not entry.peers.alive)

    async def monitor(self, revalidate):
        async with asyncio.TaskGroup() as repairs:
            while not self._closed:
                for key, entry in list(self._entries.items()):
                    if self._can_recover(entry):
                        repairs.create_task(self._recover(key, entry, revalidate))
                await asyncio.sleep(0.25)

    async def _recover(self, key, entry, revalidate):
        async with self._lock:
            if self._closed or self._entries.get(key) is not entry or not self._can_recover(entry):
                return
            del self._entries[key]
            self._pending[key] = asyncio.current_task()
        try:
            await self._start_reserved(entry.selection, key, entry.identity, entry, revalidate=revalidate)
        except (ValueError, RuntimeError, OSError, TypeError):
            print('Beta shared Project recovery failed', file=sys.stderr)

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
            if start and not entry.admitted:
                await entry.wait_ready()
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
