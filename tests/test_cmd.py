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


@pytest.mark.parametrize(
    "entrypoint, requirements, path, payload",
    [
        ("check_mimetypes.py", None, "/xyz/", '{"a": 1, "b": 2, "c": 3}'),
        ("server_t1.py", None, "/predict/", '{"val": 1}'),
    ],
)
def test_serve(entrypoint, requirements, path, payload):
    pth = os.path.join(THIS_DIR, "assets")

    def background():
        runner = CliRunner()
        runner.invoke(dc.serve, ["-e", entrypoint, "-l", pth])

    p = Process(target=background)
    p.start()
    atexit.register(p.terminate)  # in case we err somewhere
    time.sleep(1)
    r = requests.post(
        "http://localhost:8080{}".format(path),
        data=payload,
        headers={"content-type": "application/json"},
    )
    assert r.status_code == 200
    p.terminate()
