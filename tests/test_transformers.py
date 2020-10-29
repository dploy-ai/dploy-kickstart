import pytest
from flask import Response

import dploy_kickstart.transformers as dt
import dploy_kickstart.server as ds


def test_client():
    app = ds.generate_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize(
    "i, o", [("bla", '"bla"\n'), ({"foo": "bar"}, '{"foo":"bar"}\n')],
)
def test_json_resp(i, o):
    with test_client().application.test_request_context():
        r = dt.json_resp(i)
        assert r.get_data().decode() == o
        assert isinstance(r, Response)