"""Automagically generate APISpec."""

from apispec import APISpec
from dploy_kickstart.annotations import AnnotatedCallable


def base_spec(title: str) -> APISpec:
    """Generate a base APISpec."""
    spec = APISpec(title=title, version="1.0.0", openapi_version="3.0.2")
    return spec


def path_spec(spec: APISpec, ac: AnnotatedCallable) -> None:
    """Add a path to the APISpec."""
    spec.path(
        path=ac.endpoint_path,
        operations={
            ac.request_method.lower(): dict(
                requestBody={"content": {"application/json": {}}},
                responses={"200": {"content": {"application/json": {}}}},
            )
        },
    )
