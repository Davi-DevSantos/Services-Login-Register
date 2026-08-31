class AppError(Exception):
    pass

class UserNotFoundError(AppError):
    pass

class InvalidCredentialsError(AppError):
    pass

class UnauthorizedError(AppError):
    pass

class InvalidTokenError(AppError):
    pass

class ServiceUnavailableError(AppError):
    pass

class TokenExpiredError(AppError):
    pass