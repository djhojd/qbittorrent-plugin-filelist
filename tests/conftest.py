import pathlib
import sys
import types

import pytest

# Make filelist.py importable.
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# --- Fake `helpers` module (qBittorrent provides the real one) ---
_helpers = types.ModuleType('helpers')
_helpers._state = {'response': '[]', 'last_url': None}


def _retrieve_url(url, *args, **kwargs):
    _helpers._state['last_url'] = url
    resp = _helpers._state['response']
    if isinstance(resp, Exception):
        raise resp
    return resp


def _download_file(info, *args, **kwargs):
    return "/tmp/fake.torrent " + str(info)


_helpers.retrieve_url = _retrieve_url
_helpers.download_file = _download_file
sys.modules['helpers'] = _helpers

# --- Fake `novaprinter` module ---
_novaprinter = types.ModuleType('novaprinter')
_novaprinter.printed = []
_novaprinter.prettyPrinter = lambda d: _novaprinter.printed.append(d)
sys.modules['novaprinter'] = _novaprinter


@pytest.fixture
def fakes():
    """Reset fake-module state before each test; yield handles."""
    _helpers._state['response'] = '[]'
    _helpers._state['last_url'] = None
    _novaprinter.printed.clear()
    yield _helpers, _novaprinter


@pytest.fixture
def creds_file(tmp_path):
    """A valid credentials.ini in a temp dir; returns its path."""
    p = tmp_path / 'credentials.ini'
    p.write_text("[filelist]\nusername = tester\npasskey = secretkey123\n")
    return p
