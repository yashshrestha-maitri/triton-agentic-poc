"""Custom exceptions for the Triton API."""

from typing import Optional, Any


class TritonAPIException(Exception):
    """Base exception for Triton API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class TemplateNotFoundException(TritonAPIException):
    """Exception raised when a template is not found."""

    def __init__(self, template_id: str):
        super().__init__(
            message=f"Template with ID '{template_id}' not found",
            status_code=404,
            detail={"template_id": template_id}
        )


class ResultNotFoundException(TritonAPIException):
    """Exception raised when a generation result is not found."""

    def __init__(self, filename: str):
        super().__init__(
            message=f"Result file '{filename}' not found",
            status_code=404,
            detail={"filename": filename}
        )


class TemplateGenerationException(TritonAPIException):
    """Exception raised when template generation fails."""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(
            message=f"Template generation failed: {message}",
            status_code=500,
            detail=detail
        )


class ValidationException(TritonAPIException):
    """Exception raised when validation fails."""

    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(
            message=f"Validation failed: {message}",
            status_code=422,
            detail={"errors": errors} if errors else None
        )


class StorageException(TritonAPIException):
    """Exception raised when storage operations fail."""

    def __init__(self, message: str, operation: str):
        super().__init__(
            message=f"Storage operation '{operation}' failed: {message}",
            status_code=500,
            detail={"operation": operation}
        )
