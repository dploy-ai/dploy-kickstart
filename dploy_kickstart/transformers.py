"""Utilities to transform requests and responses."""
import io
import typing
from flask import jsonify, Response, Request
import dploy_kickstart.annotations as da
import dploy_kickstart.errors as pe

try:
    from PIL import Image
except ImportError as e:
    raise pe.ScriptImportError(
        f"{e}\nCannot import Pillow image library."
        + "Please add `Pillow`"
        + " to your dependencies.",
    )


def bytes_resp(func_result: typing.Any) -> Response:
    return Response(func_result, mimetype="application/octet-stream")


def bytes_io_resp(func_result: typing.Any) -> Response:
    return Response(func_result.getvalue(), mimetype="application/octet-stream")


def pil_image_resp(func_result: Image) -> Response:
    # create file-object in memory
    file_object = io.BytesIO()
    img_format = func_result.format

    # write PNG in file-object
    func_result.save(file_object, img_format)
    mimetype = f"image/{img_format.lower()}"

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)
    return Response(file_object, mimetype=mimetype)


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


MIME_TYPE_REQ_MAPPER = {True: json_req, False: default_req}

MIME_TYPE_RES_MAPPER = {
    "int": json_resp,
    "float": json_resp,
    "str": json_resp,
    "list": json_resp,
    "dict": json_resp,
    "bytes": bytes_resp,
    "BytesIO": bytes_io_resp,
    "Image": pil_image_resp,
}
