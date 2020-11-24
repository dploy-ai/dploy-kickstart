import os
import dploy_kickstart.errors as pe
import dploy_kickstart.wrapper as pw
import dploy_kickstart.server as ps
import pytest


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "package_name, expected_err_message, error_expected",
    [
        (
            "import some_random_package",
            "{'message': 'Cannot import some_random_package'}",
            True,
        ),
        ("import os", None, False),
    ],
)
def test_script_import_error(package_name, expected_err_message, error_expected):
    try:
        exec(package_name)
    except Exception as e:
        error_message = pe.ScriptImportError(f"Cannot {package_name}",).to_dict()
        assert str(error_message) == str(expected_err_message)


@pytest.mark.parametrize(
    "entrypoint, expected_err_message, error_expected",
    [
        ("golf.png", "{'message': \"entrypoint 'golf.png' not supported\"}", True),
        ("c1.py", None, False),
    ],
)
def test_unsupported_entrypoint_error(entrypoint, expected_err_message, error_expected):
    try:
        p = os.path.join(THIS_DIR, "assets")
        _ = pw.import_entrypoint(entrypoint, p)
    except Exception as e:
        assert isinstance(e, pe.UnsupportedEntrypoint)
        assert str(e.to_dict()) == str(expected_err_message)
