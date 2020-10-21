import os
import logging
import re

import pytest

import dploy_kickstart.server as ps
from io import StringIO

from .fixtures import restore_wd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", os.getenv("LOGLEVEL", "INFO")))


def test_client():
    app = ps.generate_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize(
    "entrypoint, method, path, payload, response, accept, content_type, error, status_code",
    [
        (
            "server_t1.py",
            "post",
            "/predict/",
            {"val": 1},
            1,
            "application/json",
            "application/json",
            False,
            200,
        ),
        (
            "server_t1.py",
            "post",
            "/predict",  # test without trailing slash
            {"val": 1},
            1,
            "application/json",
            "application/json",
            False,
            200,
        ),
        (
            "server_t1.py",
            "post",
            "/predict/",
            {"val": 1},
            1,
            "application/json",
            "",
            True,
            415,
        ),
        (
            "server_t1.py",
            "post",
            "/predict/",
            {"val": 1},
            1,
            "application/json",
            "application/bla",
            True,
            415,
        ),
        # not annotated
        (
            "c1_no_comments.py",
            "post",
            "/predict/",
            {"val": 1},
            1,
            "application/json",
            "application/json",
            True,
            500,
        ),
        # raise correct error when exception in user code
        (
            "c_error.py",
            "post",
            "/predict/",
            {"val": 1},
            1,
            "application/json",
            "application/json",
            True,
            500,
        ),
        # test json_to_kwargs
        (
            "check_mimetypes.py",
            "post",
            "/xyz/",
            {"a": 1, "b": 2, "c": 3},
            6,
            "application/json",
            "application/json",
            False,
            200,
        ),
    ],
)
@pytest.mark.usefixtures("restore_wd")
def test_server_generation(
    entrypoint,
    method,
    path,
    payload,
    response,
    accept,
    content_type,
    error,
    status_code,
):
    p = os.path.join(THIS_DIR, "assets")

    try:
        app = ps.generate_app()
        app = ps.append_entrypoint(app, entrypoint, p)

    except:
        assert error
        return

    test_client = app.test_client()
    if "json" in content_type:
        r = getattr(test_client, method)(
            path, json=payload, headers={"Accept": accept, "Content-Type": content_type}
        )

    else:
        r = getattr(test_client, method)(
            path, data=payload, headers={"Accept": accept, "Content-Type": content_type}
        )

    assert r.status_code == status_code

    if error:  # we expect an error here, no need to keep processing contents
        assert r.status_code != 200
        return

    if "json" in content_type:
        assert r.json == response
    else:
        assert r.data == response


@pytest.mark.parametrize(
    "entrypoint, method, path, payload, accept, content_type, str_pattern, error",
    [
        (
                "server_t1.py",
                "post",
                "/predict/",
                {"doesnt_exist": 1},
                "application/json",
                "application/json",
                "(\{'message': \"error in executing)(.*)(KeyError:).*",
                False
        ),
        # Raise different error
        (
                "server_t1.py",
                "post",
                "/predict/",
                {"doesnt_exist": 1},
                "application/json",
                "application/json",
                "(\{'message': \"error in executing)(.*)(TypeError:).*",
                True
        ),
        # 200
        (
                "server_t1.py",
                "post",
                "/predict/",
                {"val": 1},
                "application/json",
                "application/json",
                "",
                False
        )
    ],
)
@pytest.mark.usefixtures("restore_wd")
def test_server_logs(
        entrypoint,
        method,
        path,
        payload,
        accept,
        content_type,
        str_pattern,
        error
):
    p = os.path.join(THIS_DIR, "assets")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    app = ps.generate_app()
    app = ps.append_entrypoint(app, entrypoint, p)
    app.logger.addHandler(handler)
    test_client = app.test_client()
    _ = getattr(test_client, method)(
        path, json=payload, headers={"Accept": accept, "Content-Type": content_type}
    )
    str_log_stream = stream.getvalue()
    print(str_log_stream)
    try:
        assert re.match(str_pattern, str_log_stream)
    except AssertionError:
        assert error
