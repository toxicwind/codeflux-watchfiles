"""Tests for the codeflux structured-events improvement (no Rust ext needed)."""
import json

from watchfiles.codeflux import ChangeEvent


def test_change_event_json_roundtrip():
    ev = ChangeEvent(path='/x/y.py', change='modified', mtime=1.0,
                     size=10, sha256='abc', detected_at=2.0)
    d = json.loads(ev.to_json())
    assert d['path'] == '/x/y.py'
    assert d['change'] == 'modified'
    assert d['sha256'] == 'abc'
    assert d['detected_at'] == 2.0
