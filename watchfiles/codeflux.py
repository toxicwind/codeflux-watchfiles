"""Structured change events for streaming pipelines (codeflux fork improvement).

Stock watchfiles yields bare ``(Change, path)`` tuples. This module adds what a
live code-stream needs:

- :class:`ChangeEvent`: JSON-serializable record with content hash, size, mtime
- :func:`watch_events`: per-path debouncing so one save-storm becomes one event
- :func:`watch_jsonl`: print events as JSON lines, ready to pipe into
  ``codeflux`` or ``moulti stream``
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any, Iterator

from .main import Change, watch


@dataclass
class ChangeEvent:
    path: str
    change: str  # 'added' | 'modified' | 'deleted'
    mtime: float | None
    size: int | None
    sha256: str | None  # None for deleted files / unreadable files
    detected_at: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self))


def _stat_hash(path: str) -> tuple[float | None, int | None, str | None]:
    try:
        st = os.stat(path)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return st.st_mtime, st.st_size, h.hexdigest()
    except OSError:
        return None, None, None


def watch_events(*paths: str, debounce_ms: int = 500, hash_files: bool = True,
                 **watch_kwargs: Any) -> Iterator[ChangeEvent]:
    """Yield :class:`ChangeEvent` for each watched change.

    Rapid repeats on the same path inside ``debounce_ms`` are collapsed.
    All other keyword arguments pass through to :func:`watchfiles.watch`.
    """
    last_emit: dict[str, float] = {}
    for changes in watch(*paths, **watch_kwargs):
        now = time.time()
        for change, p in changes:
            if (now - last_emit.get(p, 0.0)) * 1000 < debounce_ms:
                continue
            last_emit[p] = now
            mtime, size, sha = (None, None, None)
            if change != Change.deleted and hash_files:
                mtime, size, sha = _stat_hash(p)
            yield ChangeEvent(path=p, change=change.name, mtime=mtime,
                              size=size, sha256=sha, detected_at=now)


def watch_jsonl(*paths: str, **kwargs: Any) -> None:
    """Print :func:`watch_events` output as JSON lines on stdout."""
    for ev in watch_events(*paths, **kwargs):
        sys.stdout.write(ev.to_json() + "\n")
        sys.stdout.flush()
