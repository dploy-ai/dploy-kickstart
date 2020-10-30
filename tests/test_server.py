import os
import logging
import re

import pytest

import dploy_kickstart.server as ps
from io import StringIO

from .fixtures import restore_wd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=os.environ.get("LOGLEVEL", os.getenv("LOGLEVEL", "INFO")))
PNG_IMG = open(os.path.join(THIS_DIR, "assets", "test.png"), "rb").read()
JPG_IMG = open(os.path.join(THIS_DIR, "assets", "test.jpg"), "rb").read()


def test_client():
    app = ps.generate_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize(
    "entrypoint, method, path, payload, response, accept, content_type, error, status_code",
    [
        (
            "server_bytes.py",
            "post",
            "/f1/",
            JPG_IMG,
            b'{"message":"size=1x1"}\n',
            "application/json",
            "image",
            False,
            200,
        ),
        # Wrong content-type (based on defined content-type)
        (
            "server_bytes.py",
            "post",
            "/f1/",
            JPG_IMG,
            b'{"message":"size=1x1"}\n',
            "application/json",
            "application/json",
            True,
            -1,
        ),
        (
            "server_bytes.py",
            "post",
            "/f2/",
            PNG_IMG,
            b'{"message":"image received. size=1x1"}\n',
            "application/json",
            "image",
            False,
            200,
        ),
        (
            "server_bytes.py",
            "post",
            "/f3/",
            PNG_IMG,
            PNG_IMG,
            "image",
            "image",
            False,
            200,
        ),
        (
            "server_bytes.py",
            "post",
            "/f3/",
            JPG_IMG,
            JPG_IMG,
            "image",
            "image",
            False,
            200,
        ),
        (
            "server_bytes.py",
            "post",
            "/f3/",
            JPG_IMG,
            JPG_IMG,
            "image",
            "application/json",
            True,
            -1,
        ),
        (
            "server_bytes.py",
            "post",
            "/f4/",
            PNG_IMG,
            b'{"message":"image received. size=1x1"}\n',
            "default",
            "default",
            True,
            500,
        ),
        (
            "server_bytes.py",
            "post",
            "/f5/",
            PNG_IMG,
            PNG_IMG,
            "default",
            "default",
            False,
            200,
        ),
        (
            "server_bytes.py",
            "post",
            "/f6/",
            PNG_IMG,
            PNG_IMG,
            "default",
            "default",
            False,
            200,
        ),
        (
            "server_bytes.py",
            "post",
            "/f7/",
            "foobar",
            "foobar",
            "string",
            "string",
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
            500,
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
            500,
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

    t_client = app.test_client()
    try:
        if "json" in content_type:
            r = getattr(t_client, method)(
                path,
                json=payload,
                headers={"Accept": accept, "Content-Type": content_type},
            )

        else:
            r = getattr(t_client, method)(
                path,
                data=payload,
                headers={"Accept": accept, "Content-Type": content_type},
            )
    except:
        assert error
        return

    assert r.status_code == status_code

    if error:  # we expect an error here, no need to keep processing contents
        assert r.status_code != 200
        return

    if "json" in content_type:
        assert r.json == response
    else:
        try:
            assert r.data == response
        except:
            a = 5


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
            False,
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
            True,
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
            False,
        ),
    ],
)
@pytest.mark.usefixtures("restore_wd")
def test_server_logs(
    entrypoint, method, path, payload, accept, content_type, str_pattern, error
):
    p = os.path.join(THIS_DIR, "assets")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    app = ps.generate_app()
    app = ps.append_entrypoint(app, entrypoint, p)
    app.logger.addHandler(handler)
    t_client = app.test_client()
    _ = getattr(t_client, method)(
        path, json=payload, headers={"Accept": accept, "Content-Type": content_type}
    )
    str_log_stream = stream.getvalue()

    try:
        assert re.match(str_pattern, str_log_stream)
    except AssertionError:
        assert error


@pytest.mark.parametrize(
    "path, status_code, method, error",
    [
        (
            "/healthz/",
            200,
            "get",
            False,
        ),
        (
            "/healthz",
            200,
            "get",
            False,
        ),
        (
            "/healthz/",
            200,
            "post",
            True,
        ),
        (
            "/health/",
            200,
            "get",
            True,
        ),
    ],
)
@pytest.mark.usefixtures("restore_wd")
def test_healthz(path, status_code, method, error):
    p = os.path.join(THIS_DIR, "assets")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    app = ps.generate_app()
    app = ps.append_entrypoint(app, "server_t1.py", p)
    app.logger.addHandler(handler)
    t_client = app.test_client()
    resp = getattr(t_client, method)("/healthz/")
    try:
        assert resp.status_code == status_code
    except AssertionError:
        assert error
