class DomainException(Exception):
    """
    Base exception for all domain-related errors.

    Args:
        message (str): Error message describing the exception.
        error_code (str, optional): Specific error code for the exception.
    """

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(DomainException):
    """
    Exception raised when domain validation fails.

    Args:
        message (str): Error message describing the validation failure.
        field (str, optional): The field that failed validation.
    """

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field


class EntityNotFoundError(DomainException):
    """
    Exception raised when a requested entity is not found.

    Args:
        entity_type (str): Type of the entity (e.g., "Model3D", "User").
        entity_id (str): ID of the entity that was not found.
    """

    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message, error_code="ENTITY_NOT_FOUND")
        self.entity_type = entity_type
        self.entity_id = entity_id


class BusinessRuleViolationError(DomainException):
    """
    Exception raised when a business rule is violated.

    Args:
        message (str): Error message describing the rule violation.
        rule_name (str, optional): Name of the violated business rule.
    """

    def __init__(self, message: str, rule_name: str | None = None):
        super().__init__(message, error_code="BUSINESS_RULE_VIOLATION")
        self.rule_name = rule_name


class InvalidStateError(DomainException):
    """
    Exception raised when an operation is attempted on an entity in an invalid state.

    Args:
        message (str): Error message describing the invalid state.
    """

    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_STATE")


class PrinterBusyError(DomainException):
    """
    Exception raised when a printer is busy and cannot accept a new task.

    Args:
        message (str): Error message describing the printer busy state.
    """

    def __init__(self, message: str):
        super().__init__(message, error_code="PRINTER_BUSY")
