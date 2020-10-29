import os
import logging

from pprint import pprint

import pytest
import dploy_kickstart.annotations as pa
import dploy_kickstart.openapi as po


# irrelevant comment line
#' @dploy endpoint predict
def t1():
    return 1


#' @dploy endpoint bladiebla
def t2():
    return 2


@pytest.mark.parametrize(
    "callable",
    [
        t1,
        t2,
    ],
)
def test_openapi_generation(callable):
    ca = pa.AnnotatedCallable(callable)

    s = po.base_spec("test")
    po.path_spec(s, ca)

    assert len(s.to_dict()) > 0
