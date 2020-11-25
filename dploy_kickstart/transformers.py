"""Utilities to transform requests and responses."""
import io
import typing
from fastapi import Body, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import dploy_kickstart.annotations as da


def bytes_resp(func_result: typing.Any, media_type=None) -> Response:
    if media_type is None:
        return Response(func_result, media_type="application/octet-stream")
    else:
        return Response(func_result, media_type=media_type)


def bytes_io_resp(func_result: typing.Any, media_type=None) -> Response:
    if media_type is None:
        return Response(func_result.getvalue(), media_type="application/octet-stream")
    else:
        return Response(func_result.getvalue(), media_type=media_type)


def pil_image_resp(func_result: typing.Any, media_type=None) -> Response:
    # create file-object in memory
    file_object = io.BytesIO()
    img_format = func_result.format

    # write image to a file-object
    # Don't change quality and subsampling since save decrease the quality by default
    func_result.save(file_object, img_format, quality=100, subsampling=0)
    auto_media_type = f"image/{img_format.lower()}"

    # move to beginning of file so `send_file()` it will read from start
    file_object.seek(0)

    if media_type is None:
        return Response(file_object, media_type=auto_media_type)
    else:
        return Response(file_object, media_type=media_type)


def np_tolist_resp(func_result: typing.Any, media_type=None) -> Response:
    response = jsonable_encoder(func_result.tolist())
    if media_type is None:
        return JSONResponse(response, media_type="application/json")
    else:
        return JSONResponse(response, media_type=media_type)


def np_item_resp(func_result: typing.Any, media_type=None) -> Response:
    response = jsonable_encoder(func_result.item())
    if media_type is None:
        return JSONResponse(response, media_type="application/json")
    else:
        return JSONResponse(response, media_type=media_type)


def json_resp(func_result: typing.Any, media_type=None) -> Response:
    """Transform json response."""
    response = jsonable_encoder(func_result)
    if media_type is None:
        return JSONResponse(response, media_type="application/json")
    else:
        return JSONResponse(response, media_type=media_type)


def default_req(f: da.AnnotatedCallable, body=Body(...)) -> typing.Any:
    return f(body)


def json_to_kwargs_req(f: da.AnnotatedCallable, body=Body(...)) -> typing.Any:
    return f(**body)


MIME_TYPE_REQ_MAPPER = {True: json_to_kwargs_req, False: default_req}

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
