import os
import logging

import pytest
import dploy_kickstart.annotations as pa
import dploy_kickstart.wrapper as pw

logging.basicConfig(level=os.environ.get("LOGLEVEL", os.getenv("LOGLEVEL", "INFO")))

# irrelevant comment line
#' @dploy endpoint predict
def t1():
    return 1


# no relevant comments
def t2():
    return t1()


#' @dploy endpoint /blaaa/
def t3():
    return 2


#' @dploy endpoint blaaa
# should raise an error for a non callable
t4 = 4

# ignore the '
# @dploy endpoint xyz
def t5():
    return 1


#' @dploy endpoint /with_slashes/
def t6():
    return t1()


# root path / endpoint
# @dploy endpoint
def t7():
    return t1()


@pytest.mark.parametrize(
    "callable,endpoint,endpoint_path,has_args,output, error",
    [
        (t1, True, "/predict/", True, 1, False),
        (t2, False, None, False, 1, False),
        (t3, True, "/blaaa/", True, 2, False),
        (t4, True, "/blaaa/", True, 2, True),
        (t5, True, "/xyz/", True, 1, False),
        (t6, True, "/with_slashes/", True, 1, False),
        (t7, True, "/", True, 1, False),
    ],
)
def test_callable_annotation(
    callable, endpoint, endpoint_path, has_args, output, error
):
    try:
        ca = pa.AnnotatedCallable(callable)
    except Exception:
        assert error
        return

    if endpoint_path:
        assert ca.endpoint_path == endpoint_path
    assert ca.endpoint == endpoint
    assert (len(ca.comment_args) > 0) == has_args
    ca() == output


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    "py_file,expected",
    [
        (
            "c1.py",
            [["endpoint", "predict"], ["endpoint", "train2"]],
        ),
        (
            "nb_with_comments.ipynb",
            [
                ["endpoint", "predict"],
                ["endpoint", "train"],
                ["trigger", "train"],
            ],
        ),
    ],
)
def test_annotated_scripts(py_file, expected):
    p = os.path.join(THIS_DIR, "assets")
    mod = pw.import_entrypoint(py_file, p)
    fas = pw.get_func_annotations(mod)

    flatten = lambda l: [item for sublist in l for item in sublist]
    for a in expected:
        assert a in flatten([ac.comment_args for ac in fas])


@pytest.mark.parametrize(
    "comment,expected",
    [
        [
            """
        # @dploy endpoint predict
        # @dploy widget payload_template
        #   blaat
        # @dploy widget multiwordarg
        #   "blaat says the sheep" foo "enquoted thing" bar
        # 
        # this should not parse
        """,
            [
                ["endpoint", "predict"],
                ["widget", "payload_template", "blaat"],
                [
                    "widget",
                    "multiwordarg",
                    "blaat says the sheep",
                    "foo",
                    "enquoted thing",
                    "bar",
                ],
            ],
        ],
        [
            """
        # @dploy endpoint predict
        # @dploy widget multiwordarg \
        #   "blaat says the
        # sheep"
        """,
            [
                ["endpoint", "predict"],
                ["widget", "multiwordarg", "blaat says the sheep"],
            ],
        ],
        [
            """
        # irrelevant
        # @dploy arg "foo bar" arg2 "bar the foos"
        #
        # irrelevant other stuff
        """,
            [
                ["arg", "foo bar", "arg2", "bar the foos"],
            ],
        ],
        [
            """
        # irrelevant
        #' @dploy foo
        #' @dploy foo bar
        """,
            [["foo"], ["foo", "bar"]],
        ],
        [
            """
        # irrelevant
        #' @dploy endpoint x"
        # @dploy endpoint x"
        """,
            [["endpoint", "x"], ["endpoint", "x"]],
        ],
    ],
)
def test_comment_parsing(comment, expected):
    p = pa.AnnotatedCallable.parse_comments(comment)
    assert sorted(p) == sorted(expected)
