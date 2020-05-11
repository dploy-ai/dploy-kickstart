class ServerException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class ScriptImportError(ServerException):
    status_code = 500

    def __init__(self, message: str):
        super().__init__(self)
        self.message = message

    def to_dict(self) -> dict:
        return dict(message=self.message)


class FuncArgProcessingError(ServerException):
    status_code = 500

    def __init__(self, func: str, arg: str):
        super().__init__(self, func, arg)
        self.message = "arg '{}' for func '{}'not supported".format(arg, func)

    def to_dict(self) -> dict:
        return dict(message=self.message)


class UnsupportedEntrypoint(ServerException):
    status_code = 500

    def __init__(self, entrypoint: str):
        super().__init__(self)
        self.message = "entrypoint '{}' not supported".format(entrypoint)

    def to_dict(self) -> dict:
        return dict(message=self.message)


class UnsupportedMediaType(ServerException):
    status_code = 415

    def __init__(self, message: str):
        super().__init__(self)
        self.message = message

    def to_dict(self) -> dict:
        return dict(message=self.message)


class UserApplicationError(ServerException):
    status_code = 500

    def __init__(self, message: str, traceback: str):
        super().__init__(self)
        self.message = message
        self.traceback = traceback

    def to_dict(self) -> dict:
        return dict(message=self.message, traceback=self.traceback)
