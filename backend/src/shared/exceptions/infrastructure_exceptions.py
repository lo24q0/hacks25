class InfrastructureException(Exception):
    """
    Base exception for all infrastructure-related errors.

    Args:
        message (str): Error message describing the exception.
        error_code (str, optional): Specific error code for the exception.
    """

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ExternalServiceError(InfrastructureException):
    """
    Exception raised when an external service call fails.

    Args:
        service_name (str): Name of the external service.
        message (str): Error message describing the failure.
        status_code (int, optional): HTTP status code from the service.
    """

    def __init__(self, service_name: str, message: str, status_code: int | None = None):
        super().__init__(f"{service_name} error: {message}", error_code="EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name
        self.status_code = status_code


class StorageError(InfrastructureException):
    """
    Exception raised when file storage operations fail.

    Args:
        message (str): Error message describing the storage failure.
        file_path (str, optional): Path to the file that caused the error.
    """

    def __init__(self, message: str, file_path: str | None = None):
        super().__init__(message, error_code="STORAGE_ERROR")
        self.file_path = file_path


class DatabaseError(InfrastructureException):
    """
    Exception raised when database operations fail.

    Args:
        message (str): Error message describing the database failure.
        query (str, optional): The database query that failed.
    """

    def __init__(self, message: str, query: str | None = None):
        super().__init__(message, error_code="DATABASE_ERROR")
        self.query = query


class TaskExecutionError(InfrastructureException):
    """
    Exception raised when an asynchronous task execution fails.

    Args:
        task_name (str): Name of the failed task.
        message (str): Error message describing the failure.
        retry_count (int, optional): Number of retry attempts made.
    """

    def __init__(self, task_name: str, message: str, retry_count: int = 0):
        super().__init__(f"Task '{task_name}' failed: {message}", error_code="TASK_EXECUTION_ERROR")
        self.task_name = task_name
        self.retry_count = retry_count
