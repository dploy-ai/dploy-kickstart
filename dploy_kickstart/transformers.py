"""Utilities to transform requests and responses."""

import typing
from flask import jsonify, Response, Request
import dploy_kickstart.annotations as da


def bytes_resp(func_result: typing.Any) -> Response:
    return Response(func_result, mimetype="application/octet-stream")


def bytes_io_resp(func_result: typing.Any) -> Response:
    return Response(func_result.getvalue(), mimetype="application/octet-stream")


def np_tolist_resp(func_result: typing.Any) -> Response:
    return jsonify(func_result.tolist())


def np_item_resp(func_result: typing.Any) -> Response:
    return jsonify(func_result.item())


def json_resp(func_result: typing.Any) -> Response:
    """Transform json response."""
    return jsonify(func_result)


def default_req(f: da.AnnotatedCallable, req: Request) -> typing.Any:
    return f(req.data)


def json_req(f: da.AnnotatedCallable, req: Request) -> typing.Any:
    """Preprocess application/json request."""
    if f.json_to_kwargs:
        return f(**req.json)
    else:
        return f(req.json)


MIME_TYPE_REQ_MAPPER = {True: json_req, False: default_req}

MIME_TYPE_RES_MAPPER = {
    "int": json_resp,
    "float": json_resp,
    "str": json_resp,
    "list": json_resp,
    "dict": json_resp,
    "bytes": bytes_resp,
    "BytesIO": bytes_io_resp,

    # Numpy Return dtypes
    "ndarray": np_tolist_resp,
    "matrix": np_tolist_resp,
    "int8": np_item_resp,
    "uint8": np_item_resp,
    "int16": np_item_resp,
    "uint16": np_item_resp,
    "int32": np_item_resp,
    "uint32": np_item_resp,
    "int64": np_item_resp,
    "uint64": np_item_resp,
    "float16": np_item_resp,
    "float32": np_item_resp,
    "float64": np_item_resp,
}
