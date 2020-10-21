"""Flask server logic."""

import logging
import typing

from flask import Flask, jsonify

import dploy_kickstart.wrapper as pw
import dploy_kickstart.errors as pe
import dploy_kickstart.openapi as po

log = logging.getLogger(__name__)


def append_entrypoint(app: Flask, entrypoint: str, location: str) -> Flask:
    """Add routes/functions defined in entrypoint."""
    mod = pw.import_entrypoint(entrypoint, location)
    fm = pw.get_func_annotations(mod)

    if not any([e.endpoint for e in fm]):
        raise Exception("no endpoints defined")

    openapi_spec = po.base_spec(title=entrypoint)
    # iterate over annotations in usercode
    for f in fm:
        if f.endpoint:
            log.debug(
                f"adding endpoint for func: {f.__name__} (func_args: {f.comment_args})"
            )

            app.add_url_rule(
                f.endpoint_path,
                f.endpoint_path,
                pw.func_wrapper(f),
                methods=[f.request_method.upper()],
                strict_slashes=False,
            )

            # add info about endpoint to api spec
            po.path_spec(openapi_spec, f)

    app.add_url_rule(
        "/openapi.yaml", "/openapi.yaml", openapi_spec.to_yaml, methods=["GET"],
    )

    return app


def generate_app() -> Flask:
    """Generate a Flask app."""
    app = Flask(__name__)

    @app.route("/healthz/", methods=["GET"], strict_slashes=False)
    def health_check() -> typing.Tuple[str, int]:
        return "healthy", 200

    @app.errorhandler(pe.ServerException)
    def handle_server_exception(error: pe.ServerException) -> None:
        response_dict = error.to_dict()
        response = jsonify(response_dict)
        log.error(response_dict)
        response.status_code = error.status_code
        return response

    return app
