from apispec import APISpec
from dploy_kickstart.annotations import AnnotatedCallable


def base_spec(title: str) -> APISpec:
    spec = APISpec(title=title, version="1.0.0", openapi_version="3.0.2")
    return spec


def path_spec(spec: APISpec, ac: AnnotatedCallable) -> None:
    spec.path(
        path=ac.endpoint_path,
        operations={
            ac.endpoint_method.lower(): dict(
                requestBody={"content": {"application/json": {}}},
                responses={"200": {"content": {"application/json": {}}}},
            )
        },
    )
