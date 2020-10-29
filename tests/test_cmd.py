"""Some hackytacky cli tests.

Ignoring cmd.py for coverage as they launch
long processes that are hard to include
E.g. the background processes below do not
get included in the coverage report.
"""

import os
import pytest
import requests
import atexit

import time
from multiprocessing import Process
from click.testing import CliRunner
import dploy_kickstart.cmd as dc

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OWD = os.getcwd()


@pytest.mark.parametrize(
    "entrypoint, requirements, path, payload, deps",
    [
        ("check_mimetypes.py", None, "/xyz/", '{"a": 1, "b": 2, "c": 3}', None),
        (
            "server_t1.py",
            None,
            "/predict/",
            '{"val": 1}',
            "deps_tests/requirements.txt",
        ),
    ],
)
def test_serve(entrypoint, requirements, path, payload, deps):
    pth = os.path.join(THIS_DIR, "assets")

    def background():
        runner = CliRunner()
        args = ["-e", entrypoint, "-l", pth]

        if deps:
            args = args + ["-d", deps]
        runner.invoke(dc.serve, args)

    p = Process(target=background)
    p.start()
    atexit.register(p.terminate)  # in case we err somewhere
    time.sleep(5)
    r = requests.post(
        f"http://localhost:8080{path}",
        data=payload,
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 200
    p.terminate()


DEPS_CASES = [
    ("req1.txt", ".", True),
    ("", ".", False),
    ("requirements.txt", ".", False),
    ("../deps_tests/requirements.txt", ".", False),  # relative location
    ("setup.py", "my_pkg", False),
    ("setup.py", "doesnt_exist", True),
    ("my_pkg/setup.py", ".", False),
    ("setup_not_supported.py", ".", True),
]


@pytest.mark.parametrize("deps, location, should_err", DEPS_CASES)
def test_install_deps(deps, location, should_err):
    rnr = CliRunner()
    pth = os.path.join(THIS_DIR, "assets/deps_tests", location)
    res = rnr.invoke(dc.cli, ["install-deps", "-d", deps, "-l", pth])

    if should_err:
        assert res.exit_code > 0
    else:
        assert res.exit_code == 0


@pytest.mark.parametrize(
    "deps, location, should_err",
    [
        ("requirements.txt", "assets/deps_tests", False),
        ("requirements.txt", "assets/doesnt_exist", True),
        ("doesnt_exist.txt", "assets/deps_tests", True),
    ],
)
def test_install_deps_loc(deps, location, should_err):
    rnr = CliRunner()
    pth = os.path.join(THIS_DIR, location)
    res = rnr.invoke(dc.cli, ["install-deps", "-d", deps, "-l", pth])

    if should_err:
        assert res.exit_code > 0
    else:
        assert res.exit_code == 0


@pytest.mark.parametrize("deps, location, should_err", DEPS_CASES)
def test_install_deps_rel(deps, location, should_err):
    ## test relative locations
    rnr = CliRunner()
    rel_pth = os.path.join(OWD, "./tests/", "assets/deps_tests", location)
    res = rnr.invoke(dc.cli, ["install-deps", "-d", deps, "-l", rel_pth])

    if should_err:
        assert res.exit_code > 0
    else:
        assert res.exit_code == 0


@pytest.mark.parametrize("deps, location, should_err", DEPS_CASES)
def test___deps(deps, location, should_err):
    pth = os.path.join(THIS_DIR, "assets/deps_tests", location)
    try:
        dc._deps(deps, pth)
    except:
        assert should_err
