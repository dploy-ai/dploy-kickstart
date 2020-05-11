import os
import logging

import pytest
import dploy_kickstart.wrapper as pw

logging.basicConfig(level=os.environ.get("LOGLEVEL", os.getenv("LOGLEVEL", "INFO")))
THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "py_file,func,expected",
    [
        ("test_returned_result.py", "f1", 1),
        ("test_returned_result.py", "f2", 2),
        ("test_func_exec_nb.ipynb", "f1", 1),
        ("test_func_exec_nb.ipynb", "f2", 2),
    ],
)
def test_func_exec(py_file, func, expected):
    p = os.path.join(THIS_DIR, "assets")
    mod = pw.import_entrypoint(py_file, p)

    assert mod.__getattribute__(func)() == expected
