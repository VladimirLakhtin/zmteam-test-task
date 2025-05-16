class CRUDException(Exception):
    """Base exception for CRUD operations."""


class NotFoundError(CRUDException):
    """Raised when an object is not found."""


class CreateError(CRUDException):
    """Raised when an object cannot be created."""


class UpdateError(CRUDException):
    """Raised when an object cannot be updated."""


class DeleteError(CRUDException):
    """Raised when an object cannot be deleted."""