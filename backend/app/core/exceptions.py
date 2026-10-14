"""Domain exceptions. The API layer maps them to HTTP responses in one place (app/main.py)."""


class AppError(Exception):
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationFailed(AppError):
    status_code = 422


class InsufficientDataError(ValidationFailed):
    """Not enough valid observations to compute a reliable result."""


class NotFoundError(AppError):
    status_code = 404


class UpstreamServiceError(AppError):
    status_code = 502
