import pytest
import os
import dploy_kickstart.transformers as dt
import dploy_kickstart.server as ds
from io import BytesIO
from flask import Response
from PIL import Image

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_IMG = open(os.path.join(THIS_DIR, "assets", "test.png"), "rb").read()
PIL_IMG = Image.open(BytesIO(BIN_IMG))


def test_client():
    app = ds.generate_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize(
    "i, o, mimetype, expected_mimetype, error_expected",
    [
        ("bla", '"bla"\n', None, "application/json", False),
        ({"foo": "bar"}, '{"foo":"bar"}\n', None, "application/json", False),
        (
            {"foo1": "bar1"},
            '{"foo1":"bar1"}\n',
            "application/json",
            "application/json",
            False,
        ),
        ({"foo2": "bar2"}, '{"foo2":"bar2"}\n', "text/data", "text/data", False),
        ({"foo2": "bar2"}, '{"foo2":"bar2"}\n', "application/json", "text/data", True),
        ({"foo2": "bar2"}, '{"foo2":"bar2"}\n', None, "text/data", True),
        ({"foo2": "bar2"}, '{"foo2":"bar2"}\n', None, None, True),
    ],
)
def test_json_resp(i, o, mimetype, expected_mimetype, error_expected):
    with test_client().application.test_request_context():
        r = dt.json_resp(i, mimetype=mimetype)
        try:
            assert r.get_data().decode() == o
            assert r.mimetype == expected_mimetype
            assert isinstance(r, Response)
        except Exception as e:
            assert error_expected


@pytest.mark.parametrize(
    "i, o, mimetype, expected_mimetype, error_expected",
    [
        (BytesIO(BIN_IMG), BIN_IMG, None, "application/octet-stream", False),
        (BytesIO(BIN_IMG), b"", None, "application/octet-stream", True),
        (
            BytesIO(BIN_IMG),
            BIN_IMG,
            "application/octet-stream",
            "application/octet-stream",
            False,
        ),
        (BytesIO(BIN_IMG), BIN_IMG, "image/png", "application/octet-stream", True),
        (BytesIO(BIN_IMG), BIN_IMG, "image/png", "image/png", False),
        (BytesIO(BIN_IMG), BIN_IMG, "image/png", "image/jpg", True),
    ],
)
def test_bytes_io_resp(i, o, mimetype, expected_mimetype, error_expected):
    with test_client().application.test_request_context():
        r = dt.bytes_io_resp(i, mimetype=mimetype)
        try:
            assert r.get_data() == o
            assert r.mimetype == expected_mimetype
            assert isinstance(r, Response)
        except Exception as e:
            assert error_expected


@pytest.mark.parametrize(
    "i, o, mimetype, expected_mimetype, error_expected",
    [
        (BIN_IMG, BIN_IMG, None, "application/octet-stream", False),
        (BIN_IMG, b"", None, "application/octet-stream", True),
        (
            BIN_IMG,
            BIN_IMG,
            "application/octet-stream",
            "application/octet-stream",
            False,
        ),
        (BIN_IMG, BIN_IMG, "image/png", "application/octet-stream", True),
        (BIN_IMG, BIN_IMG, "image/png", "image/png", False),
        (BIN_IMG, BIN_IMG, "image/png", "image/jpg", True),
    ],
)
def test_bytes_resp(i, o, mimetype, expected_mimetype, error_expected):
    with test_client().application.test_request_context():
        r = dt.bytes_resp(i, mimetype=mimetype)
        try:
            assert r.get_data() == o
            assert r.mimetype == expected_mimetype
            assert isinstance(r, Response)
        except Exception as e:
            assert error_expected


@pytest.mark.parametrize(
    "i, mimetype, expected_mimetype, error_expected",
    [
        (PIL_IMG, None, "image/png", False),
        (PIL_IMG, "application/octet-stream", "application/octet-stream", False),
        (PIL_IMG, "image/png", "application/octet-stream", True),
        (PIL_IMG, "image/png", "image/png", False),
        (PIL_IMG, "image/jpeg", "image/jpeg", False),
        (PIL_IMG, "image/png", "image/jpg", True),
    ],
)
def test_pil_img_resp(i, mimetype, expected_mimetype, error_expected):
    with test_client().application.test_request_context():
        r = dt.pil_image_resp(i, mimetype=mimetype)
        o = Image.open(BytesIO(r.get_data()))
        try:
            assert list(i.getdata()) == list(o.getdata())
            assert r.mimetype == expected_mimetype
            assert isinstance(r, Response)
        except Exception as e:
            assert error_expected
