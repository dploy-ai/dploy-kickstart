"""CLI commands."""

import os
import logging
import typing
import signal

import click
from waitress import serve as waitress_serve
from paste.translogger import TransLogger

from dploy_kickstart import deps as pd
from dploy_kickstart import server as ps


log = logging.getLogger(__name__)


def handle_sigterm(*args):
    click.echo("Received SIGTERM")
    raise KeyboardInterrupt()


@click.group()
def cli() -> None:
    """CLI entrypoint."""
    pass


@cli.command(help="run dploy_kickstart server")
@click.option(
    "-e", "--entrypoint", required=True, help=".py or .ipynb to use as entrypoint"
)
@click.option(
    "-l",
    "--location",
    required=True,
    help="location of the script or notebook (and that will "
    + "be used as execution context)",
)
@click.option(
    "-d",
    "--deps",
    help="install dependencies; comma separated paths to either requirements.txt "
    + "or setup.py files. note that this can be run seperately via the "
    + "'install-deps' command",
)
@click.option(
    "--wsgi/--no-wsgi",
    default=True,
    help="Use Waitress as a WSGI server, defaults to True,"
    + " else launches a Flask debug server.",
)
@click.option(
    "-h", "--host", help="Host to serve on, defaults to '0.0.0.0'", default="0.0.0.0"
)
@click.option(
    "-p", "--port", help="Port to serve on, defaults to '8080'", default=8080, type=int
)
def serve(
    entrypoint: str, location: str, deps: str, wsgi: bool, host: str, port: int
) -> typing.Any:
    """CLI serve."""
    if deps:
        click.echo(f"Installing deps: {deps}")
        _deps(deps, location)

    signal.signal(signal.SIGTERM, handle_sigterm)

    app = ps.generate_app()
    app = ps.append_entrypoint(app, entrypoint, os.path.abspath(location))

    if not wsgi:
        click.echo("Starting Flask Development server")
        app.run(
            host=os.getenv("DPLOY_KICKSTART_HOST", "0.0.0.0"),
            port=int(os.getenv("DPLOY_KICKSTART_PORT", 8080)),
        )
    else:
        click.echo("Starting Waitress server")
        waitress_serve(
            TransLogger(app, setup_console_handler=False),
            host=os.getenv("dploy_kickstart_HOST", "0.0.0.0"),
            port=int(os.getenv("dploy_kickstart_PORT", 8080)),
        )


@cli.command(help="install dependencies")
@click.option(
    "-d",
    "--deps",
    required=True,
    help="comma separated paths to either requirements.txt or setup.py files",
)
@click.option(
    "-l",
    "--location",
    default=".",
    required=False,
    help="location of the script or notebook (and that will "
    + "be used as execution context). Will default to '.'",
)
def install_deps(deps: str, location: str) -> None:
    """CLI install dependencies."""
    click.echo(f"Installing deps... {deps}")
    _deps(deps, location)


def _deps(deps: str, location: str) -> None:
    """Install deps."""
    for r in deps.split(","):
        if not r:
            pass  # to allow to pass empty string when use in templated manner
        elif r.endswith("requirements.txt"):
            pd.install_requirements_txt(os.path.abspath(os.path.join(location, r)))
        elif r.endswith("setup.py"):
            pd.install_setup_py(os.path.abspath(os.path.join(location, r)))
        else:
            raise Exception(
                "unsupported dependency install defined: {}. "
                "Supported formats: "
                "requirements.txt, setup.py".format(r)
            )
