"""Utilities to transform requests and responses."""

import typing
from flask import jsonify, Response


def json_resp(func_result: typing.Any) -> Response:
    """Transform json response."""
    if type(func_result) == str:
        return func_result
    else:
        return jsonify(func_result)


MIME_TYPE_REQ_MAPPER = {
    "application/json": lambda f, req: f(req.json),
}

MIME_TYPE_RES_MAPPER = {
    "application/json": json_resp,
}
