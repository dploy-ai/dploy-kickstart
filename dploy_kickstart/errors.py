"""Custom error definitions."""
# flake8: noqa


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


class UnsupportedEntrypoint(ServerException):
    status_code = 500

    def __init__(self, entrypoint: str):
        super().__init__(self)
        self.message = f"entrypoint '{entrypoint}' not supported"

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
