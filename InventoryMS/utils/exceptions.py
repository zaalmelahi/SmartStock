class ProjectBaseException(Exception):
    """Base category for all project-specific exceptions."""
    message = "An unexpected error occurred."
    status_code = 500

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message or self.message)
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload

class BusinessLogicException(ProjectBaseException):
    """Exception raised for errors in the business logic."""
    message = "A business logic error occurred."
    status_code = 400

class ValidationException(ProjectBaseException):
    """Exception raised for validation errors."""
    message = "Validation failed."
    status_code = 422

class AuthenticationException(ProjectBaseException):
    """Exception raised for authentication errors."""
    message = "Authentication failed."
    status_code = 401

class ResourceNotFoundException(ProjectBaseException):
    """Exception raised when a resource is not found."""
    message = "Resource not found."
    status_code = 404

class PermissionDeniedException(ProjectBaseException):
    """Exception raised when permission is denied."""
    message = "Permission denied."
    status_code = 403
