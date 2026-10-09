import os
import tempfile

import pytest

# Keep this project's own test runs from touching your real capybara.
os.environ.setdefault("MICAPYBARA_HOME", tempfile.mkdtemp(prefix="micapybara-tests-"))


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("MICAPYBARA_HOME", str(tmp_path))
    return tmp_path
