import pytest
import os
import dploy_kickstart.transformers as dt
import dploy_kickstart.server as ds
import numpy as np
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


@pytest.mark.parametrize(
    "i, o, mimetype, expected_mimetype, error_expected",
    [
        # Tests for ndarray
        (np.array([1, 2, 3]), [1, 2, 3], None, "application/json", False),
        (np.array([1, 2, 3]), [222, 2222, 222], None, "application/json", True),
        (np.array([1, 2, 3]), [1, 2, 3], "application/json", "application/json", False),
        (np.array([1, 2, 3]), [1, 2, 3], "application/json", "data/text", True),
        (np.array([1, 2, 3]), b"[1,2,3]\n", "data/text", "data/text", False),
        (np.array([1, 2, 3]), b"[1,2,3]\n", None, "data/text", True),
        # Tests for matrix
        (np.matrix([1, 2, 3]), [[1, 2, 3]], None, "application/json", False),
        (np.matrix([1, 2, 3]), [[222, 2222, 222]], None, "application/json", True),
        (
            np.matrix([1, 2, 3]),
            [[1, 2, 3]],
            "application/json",
            "application/json",
            False,
        ),
        (np.matrix([1, 2, 3]), [[1, 2, 3]], "application/json", "data/text", True),
        (np.matrix([1, 2, 3]), b"[[1,2,3]]\n", "data/text", "data/text", False),
        (np.matrix([1, 2, 3]), b"[[1,2,3]]\n", None, "data/text", True),
    ],
)
def test_numpy_list_resp(i, o, mimetype, expected_mimetype, error_expected):
    with test_client().application.test_request_context():
        r = dt.np_tolist_resp(i, mimetype=mimetype)
        if mimetype is None or mimetype == "application/json":
            data = r.json
        else:
            data = r.get_data()
        try:
            assert data == o
            assert r.mimetype == expected_mimetype
            assert isinstance(r, Response)
        except Exception as e:
            assert error_expected


@pytest.mark.parametrize(
    "i, o, mimetype, expected_mimetype, error_expected",
    [
        # Check all numpy dtypes
        (np.int8(61), 61, None, "application/json", False),
        (np.uint8(61), 61, None, "application/json", False),
        (np.int16(61), 61, None, "application/json", False),
        (np.uint16(61), 61, None, "application/json", False),
        (np.int32(61), 61, None, "application/json", False),
        (np.uint32(61), 61, None, "application/json", False),
        (np.int64(61), 61, None, "application/json", False),
        (np.uint64(61), 61, None, "application/json", False),
        (np.float16(61), 61, None, "application/json", False),
        (np.float32(61), 61, None, "application/json", False),
        (np.float64(61), 61, None, "application/json", False),
        # Some problematic examples
        (np.float64(61), np.float64(61), None, "application/json", True),
        (np.float64(61), 61, "text/data", "application/json", True),
        # Different Mimetypes
        (np.float64(61), b"61.0\n", "text/data", "text/data", False),
    ],
)
def test_numpy_item_resp(i, o, mimetype, expected_mimetype, error_expected):
    with test_client().application.test_request_context():
        r = dt.np_item_resp(i, mimetype=mimetype)
        if mimetype is None or mimetype == "application/json":
            data = r.json
        else:
            data = r.get_data()
        try:
            assert data == o
            assert r.mimetype == expected_mimetype
            assert isinstance(r, Response)
        except Exception as e:
            assert error_expected
