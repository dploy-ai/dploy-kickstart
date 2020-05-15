"""Function annotations processors."""

import inspect
import typing
import re

import dploy_kickstart.transformers as dt
import dploy_kickstart.errors as de


class AnnotatedCallable:
    """Wrap a callable and allow annotation (comments) extraction."""

    def __init__(self, callble: typing.Callable) -> None:
        """Init class by passing callable."""
        # avoid shadowing 'callable' method
        self.callble = callble

        self.comment_args = []

        self.endpoint = False
        self.endpoint_path = None
        self.request_method = "post"
        self.accepts_json = True
        self.returns_json = True
        self.response_mime_type = "application/json"
        self.request_content_type = "application/json"
        self.json_to_kwargs = False

        if not callable(callble):
            raise Exception("Trying to parse annotations on non-callable object")

        comments = inspect.getcomments(callble)
        self.comment_args = self.parse_comments(comments)
        self.evaluate_comment_args()

    @staticmethod
    def parse_comments(cs: str) -> None:
        """Parse comments."""
        args = []
        if not cs:
            return args

        # remove #
        cs = cs.replace("#", "")
        rexp = r"@dploy(.*?)(?=@dploy|^\s*$)"

        # iterate over arguments
        for m in re.finditer(rexp, cs, re.MULTILINE | re.DOTALL):
            arg = m.group(1)
            # remove redundant whitespace
            arg = " ".join(arg.split())
            args.append(slice_n_dice(arg))
        return args

    def evaluate_comment_args(self) -> None:
        """Evaluate comments and act accordingly."""
        for c in self.comment_args:
            if c[0] == "endpoint":
                if len(c) > 1:
                    p = f"/{c[1]}/"
                else:
                    p = "/"

                # clean up path
                p = p.replace("//", "/")

                self.endpoint = True
                self.endpoint_path = p

            if c[0] == "response_mime_type":
                if not c[1].lower() in dt.MIME_TYPE_RES_MAPPER.keys():
                    raise de.UnsupportedMediaType(
                        "unsupported response_mime_type set for function {}".format(
                            self.callble.__name__
                        )
                    )
                self.response_mime_type = c[1].lower()

            if c[0] == "request_content_type":
                if not c[1].lower() in dt.MIME_TYPE_REQ_MAPPER.keys():
                    raise de.UnsupportedMediaType(
                        "unsupported request_content_type set for function {}".format(
                            self.callble.__name__
                        )
                    )
                self.request_content_type = c[1].lower()

            if c[0] == "request_method":
                self.request_method = c[1].lower()

            if c[0] == "json_to_kwargs":
                self.json_to_kwargs = True

    def has_args(self) -> bool:
        """Return if callable has comment annotation arguments."""
        return len(self.comment_args) > 0

    def __call__(self, *args, **kwargs) -> typing.Any:
        """Allow calling of original callable."""
        return self.callble(*args, **kwargs)

    def __name__(self) -> str:
        """Return name of original callable."""
        return self.callble.__name__


def slice_n_dice(s: str) -> list:
    """Parse quotes within strings as separate slices."""
    in_quotes = False
    slice_points = []
    slice_start = 0
    b = None
    for i, c in enumerate(s):
        if slice_start >= i:
            continue

        elif s[i : i + 2] in [' "', '" ']:
            slice_points.append((slice_start, i))
            in_quotes = not in_quotes
            slice_start = i + 2

        elif c == '"':
            in_quotes = not in_quotes
            slice_points.append((slice_start, i))
            slice_start = i + 1

        elif c == " " and not in_quotes:
            slice_points.append((slice_start, i))
            slice_start = i + 1

        elif i == len(s) - 1:
            slice_points.append((slice_start, i + 1))

    slices = []
    for a, b in slice_points:
        slices.append(s[a:b])

    return slices
