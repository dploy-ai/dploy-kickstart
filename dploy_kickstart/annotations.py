import inspect
import typing
import re


class AnnotatedCallable:
    def __init__(self, callble: typing.Callable) -> None:
        # avoid shadowing 'callable' method
        self.callble = callble

        self.comment_args = []

        self.endpoint = False
        self.endpoint_path = None
        self.endpoint_method = "POST"
        self.accepts_json = True
        self.returns_json = True

        if not callable(callble):
            raise Exception("Trying to parse annotations on non-callable object")

        comments = inspect.getcomments(callble)
        self.comment_args = self.parse_comments(comments)
        self.evaluate_comment_args()

    # def fetch_comments(self) -> None:
    #     cs = inspect.getcomments(self.callble)
    #     if cs:
    #         for c in cs.splitlines():
    #             args = self.clean_comment(c)
    #             if args:
    #                 self.comment_args.append(args)

    @staticmethod
    def parse_comments(cs: str) -> None:
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

    # @staticmethod
    # def clean_comment(c: str) -> typing.List:
    #     # ignore all annotations that do not follow this signature
    #     if "#' @dploy " not in c:
    #         return
    #     # func args are defined in form of "#' @dploy arg1 arg2 arg3"
    #     # strip off prefix
    #     c = c.split("#' @dploy ", 1)[-1]
    #     # clean up whitespaces
    #     c = c.strip()
    #     # generate list of args
    #     return c.split(" ")

    def evaluate_comment_args(self) -> None:
        for c in self.comment_args:
            if c[0] == "endpoint":
                self.endpoint = True
                self.endpoint_path = "/{}/".format(c[1])

    def has_args(self) -> bool:
        return len(self.comment_args) > 0

    def __call__(self, *args, **kwargs) -> typing.Any:
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
