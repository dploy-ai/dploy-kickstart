import os
import logging

import pytest
import dploy_kickstart.wrapper as pw

logging.basicConfig(level=os.environ.get("LOGLEVEL", os.getenv("LOGLEVEL", "INFO")))
THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "py_file,expect_exception",
    [
        ("test1.py", False),
        ("c1.py", False),
        ("subfolder/c1.py", False),
        ("test1-does-not-exist.py", True),
    ],
)
def test_import(py_file, expect_exception):
    p = os.path.join(THIS_DIR, "assets")
    try:
        mod = pw.import_entrypoint(py_file, p)
        assert expect_exception == False
    except Exception:
        assert expect_exception == True
