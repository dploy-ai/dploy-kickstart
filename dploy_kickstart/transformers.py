"""Utilities to transform requests and responses."""

import typing
from flask import jsonify, Response, Request

import dploy_kickstart.annotations as da


def json_resp(func_result: typing.Any) -> Response:
    """Transform json response."""
    return jsonify(func_result)


def json_req(f: da.AnnotatedCallable, req: Request):
    """Preprocess application/json request."""
    if f.json_to_kwargs:
        return f(**req.json)
    else:
        return f(req.json)


MIME_TYPE_REQ_MAPPER = {
    "application/json": json_req,
}

MIME_TYPE_RES_MAPPER = {
    "application/json": json_resp,
}
