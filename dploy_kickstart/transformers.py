"""Utilities to transform requests and responses."""
import io
import typing
from flask import jsonify, Response, Request
import dploy_kickstart.annotations as da


def bytes_resp(func_result: typing.Any, mimetype=None) -> Response:
    if mimetype is None:
        return Response(func_result, mimetype="application/octet-stream")
    else:
        return Response(func_result, mimetype=mimetype)


def bytes_io_resp(func_result: typing.Any, mimetype=None) -> Response:
    if mimetype is None:
        return Response(func_result.getvalue(), mimetype="application/octet-stream")
    else:
        return Response(func_result.getvalue(), mimetype=mimetype)


def pil_image_resp(func_result: typing.Any, mimetype=None) -> Response:
    # create file-object in memory
    file_object = io.BytesIO()
    img_format = func_result.format

    # write image to a file-object
    # Don't change quality and subsampling since save decrease the quality by default
    func_result.save(file_object, img_format, quality=100, subsampling=0)
    auto_mimetype = f"image/{img_format.lower()}"

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)

    if mimetype is None:
        return Response(file_object, mimetype=auto_mimetype)
    else:
        return Response(file_object, mimetype=mimetype)


def np_tolist_resp(func_result: typing.Any, mimetype=None) -> Response:
    response = jsonify(func_result.tolist())
    if mimetype is None:
        return response
    else:
        response.mimetype = mimetype
        return response


def np_item_resp(func_result: typing.Any, mimetype=None) -> Response:
    response = jsonify(func_result.item())
    if mimetype is None:
        return response
    else:
        response.mimetype = mimetype
        return response


def json_resp(func_result: typing.Any, mimetype=None) -> Response:
    """Transform json response."""
    response = jsonify(func_result)
    if mimetype is None:
        return response
    else:
        response.mimetype = mimetype
        return response


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
    # io.BytesIO return type
    "BytesIO": bytes_io_resp,
    # Pillow Image Return dtype
    "Image": pil_image_resp,
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
