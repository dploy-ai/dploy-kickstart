import os
import dploy_kickstart.deps as pd
import pytest
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PY_VERSION = str(sys.version_info.major) + "." + str(sys.version_info.minor)


@pytest.mark.parametrize(
    "req_file, error_expected",
    [("req1.txt", True), ("non_existing.txt", True), ("requirements.txt", False),],
)
def test_req_install(req_file, error_expected):
    p = os.path.join(THIS_DIR, "assets", "deps_tests")
    try:
        pd.install_requirements_txt(os.path.join(p, req_file))
    except Exception as e:
        assert error_expected
        assert isinstance(e, pd.RequirementsInstallException)


@pytest.mark.parametrize(
    "setup_py, error_expected",
    [("my_pkg/setup.py", False), ("non_existing_pkg/setup.py", True),],
)
def test_setuppy_install(setup_py, error_expected):
    p = os.path.join(THIS_DIR, "assets", "deps_tests")
    try:
        pd.install_setup_py(os.path.join(p, setup_py))
    except Exception as e:
        assert error_expected
        assert isinstance(e, pd.SetupPyInstallException)
