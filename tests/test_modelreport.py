import os
import logging
import pytest
import dploy_kickstart.server as ps
import dploy_kickstart.annotations as da
from .fixtures import restore_wd
import json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", os.getenv("LOGLEVEL", "INFO")))


def test_client():
    app = ps.generate_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize(
    "entrypoint,method,path,payload,report_header_value",
    [
        (
            "server_t1.py",
            "post",
            "/performance/",
            {"val": 1},
            {"_performance": {"val": 1}},
        ),
    ],
)
@pytest.mark.usefixtures("restore_wd")
def test_report_header(entrypoint, method, path, payload, report_header_value):
    p = os.path.join(THIS_DIR, "assets")

    try:
        app = ps.generate_app()
        app = ps.append_entrypoint(app, entrypoint, p)

    except:
        assert error
        return

    test_client = app.test_client()
    r = getattr(test_client, method)(
        path, json=payload, headers={"Content-Type": "application/json"}
    )

    assert r.status_code == 200
    assert json.loads(r.headers.get(da.HEADER_MODEL_REPORT)) == report_header_value
