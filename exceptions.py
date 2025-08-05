class AppError(Exception):
    """Base app exception"""

class TickerNotFoundError(AppError):
    pass

class InvalidTransactionError(AppError):
    pass

class InsufficientQuantityError(AppError):
    pass

class RepositoryError(AppError):
    pass
