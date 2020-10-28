"""Utilities to transform requests and responses."""

import typing
from flask import jsonify, Response, Request, send_file

import dploy_kickstart.annotations as da


def image_resp(func_result: typing.Any) -> Response:
    """Transform byte image response."""
    # Note that mime_type is image/png and it's a placeholder for images
    # both image/png, image/jpeg, image/gif are supported
    return send_file(func_result, mimetype='image/png')


def image_req(f: da.AnnotatedCallable, req: Request) -> typing.Any:
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
    "image": image_req
}

MIME_TYPE_RES_MAPPER = {
    "application/json": json_resp,
    "image": image_resp
}
