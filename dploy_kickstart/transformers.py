"""Utilities to transform requests and responses."""

import typing
import traceback
from flask import jsonify, Response, Request
from io import BytesIO
import dploy_kickstart.annotations as da
import dploy_kickstart.errors as de


def default_resp(func_result: typing.Any) -> Response:
    """Transform byte stream response."""
    if isinstance(func_result, bytes):
        return func_result
    elif isinstance(func_result, BytesIO):
        return func_result.getvalue()
    else:
        try:
            return json_resp(func_result)
        except Exception:
            raise de.UserApplicationError(
                message="Only `bytes`, `io.BytesIO` or `JSON` compatible"
                " data types can be provided as a valid return type"
                " for your dploy annotated methods.",
                traceback=traceback.format_exc(),
            )


def default_req(f: da.AnnotatedCallable, req: Request) -> typing.Any:
    return f(req.data)


def json_resp(func_result: typing.Any) -> Response:
    """Transform json response."""
    return jsonify(func_result)


def json_req(f: da.AnnotatedCallable, req: Request) -> typing.Any:
    """Preprocess application/json request."""
    if f.json_to_kwargs:
        return f(**req.json)
    else:
        return f(req.json)


MIME_TYPE_REQ_MAPPER = {
    "application/json": json_req,
    "image": default_req,
    "default": default_req,
}

MIME_TYPE_RES_MAPPER = {
    "application/json": json_resp,
    "image": default_resp,
    "default": default_resp,
}
