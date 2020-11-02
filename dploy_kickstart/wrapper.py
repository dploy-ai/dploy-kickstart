"""Function wrapping logic."""

import importlib
import os
import sys
import logging
import tempfile
import atexit
import functools
import typing
import traceback

from flask import request
import dploy_kickstart.errors as pe

import dploy_kickstart.transformers as pt
import dploy_kickstart.annotations as pa


log = logging.getLogger(__name__)


def nb_to_py(nb_file: str, location: str) -> str:
    """Convery .ipynb to temporary .py file."""
    try:
        import nbformat
        import nbconvert
    except ImportError as e:
        raise pe.ScriptImportError(
            f"{e}\nCannot import notebook conversion libraries."
            + "Please add `jupyter` (or `nbformat` and `nbconvert`)"
            + " to your dependencies.",
        )

    handle, filename = tempfile.mkstemp(text=True, suffix=".py")
    with os.fdopen(handle, "w") as tf:

        with open(os.path.join(location, nb_file)) as fh:
            nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)

        exporter = nbconvert.PythonExporter()
        src, _ = exporter.from_notebook_node(nb)

        tf.writelines(src)

        # delete file on exit
        atexit.register(functools.partial(os.remove, filename))

    return os.path.basename(filename), os.path.dirname(filename)


def get_func_annotations(mod: typing.Generic) -> typing.List[pa.AnnotatedCallable]:
    """Scan usercode for function annotations."""
    cm = []
    # check which functions have relevant args and return 'em
    for name, val in mod.__dict__.items():
        if callable(val):
            ac = pa.AnnotatedCallable(val)
            if ac.has_args():
                cm.append(ac)
    return cm


def import_entrypoint(entrypoint: str, location: str) -> typing.Generic:
    """Import entrypoint from user code."""
    # assert if entrypoint contains a path prefix and if so add it to location
    if os.path.dirname(entrypoint) != "":
        location = os.path.join(location, os.path.dirname(entrypoint))
        entrypoint = os.path.basename(entrypoint)

    # add location to path for mod importing
    sys.path.insert(0, location)
    # switch to location to allow for relative asset loading in usercode
    os.chdir(location)

    _, ext = os.path.splitext(entrypoint)
    if ext == ".ipynb":
        entrypoint, location = nb_to_py(entrypoint, location)
        # add location of temporary .py file so it can be imported
        sys.path.insert(0, location)
    elif ext == ".py":
        pass
    else:
        log.error(f"unsupportered entrypoint: {entrypoint}")
        raise pe.UnsupportedEntrypoint(entrypoint)

    mod_file, _ = os.path.splitext(entrypoint)

    msg = "loading module '{}' (modfile: {}) from location '{}'".format(
        entrypoint, mod_file, location
    )
    log.debug(msg)

    try:
        mod = importlib.import_module(mod_file, location)
    except Exception as e:
        raise pe.ScriptImportError(f"{msg}: {e}")

    return mod


def func_wrapper(f: pa.AnnotatedCallable) -> typing.Callable:
    """Wrap functions with request logic."""

    def exposed_func() -> typing.Callable:
        # preprocess input for callable
        try:
            res = pt.MIME_TYPE_REQ_MAPPER[request.is_json](f, request)
        except Exception:
            raise pe.UserApplicationError(
                message=f"error in executing '{f.__name__()}' method.",
                traceback=traceback.format_exc(),
            )

        # determine whether or not to process response before sending it back to caller
        try:
            return pt.MIME_TYPE_RES_MAPPER[res.__class__.__name__](res)
        except Exception:
            raise pe.UserApplicationError(
                message=f"error in executing '{f.__name__()}' method, the return type "
                f"{res.__class__.__name__} is not supported",
                traceback=traceback.format_exc(),
            )

    return exposed_func
